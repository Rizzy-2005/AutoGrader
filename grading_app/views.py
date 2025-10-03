# grading_app/views.py
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings 
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
import google.generativeai as genai
import json
import re

from .forms import UploadForm 
from .models import Upload, GradingResult 

User = get_user_model()

# ===============================================
# AUTHENTICATION VIEWS
# ===============================================

# --- Suggested structure for views.py ---


# from .models import AssignmentUpload, GradingResult  # Import your models



def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_type = request.POST.get("role")  # teacher/student from your form

        # ✅ Check uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, "signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        # ✅ Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("/login/")

    return render(request, "signup.html")


def landing(request):
    return render(request, "landing.html")

def about(request):
    return render(request, "about.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            from django.contrib.auth import login as auth_login
            auth_login(request, user)

            if user.user_type == "teacher":
                return redirect("teacher_dashboard")
            elif user.user_type == "student":
                return redirect("student_dashboard")
    return render(request, "login.html")



def logout(request):
    # Call Django’s built-in logout function
    auth_logout(request)
    # Redirect user to login page after logout
    return redirect('/login/')

def student_dashboard(request):
    return render(request, "student_dashboard.html")

# ===============================================
# GEMINI GRADING LOGIC
# ===============================================

def configure_gemini():
    """Sets up and returns the Gemini model."""
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        print("FATAL ERROR: GEMINI_API_KEY not found in settings.py")
        raise ValueError("GEMINI_API_KEY not configured.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-pro") 

# def extract_and_grade_with_gemini(upload_instance):
#     """Core function to run the Gemini API call and save results."""
    
#     gemini_model = configure_gemini()
    
#     # 1. Read File Bytes
#     try:
#         qp_bytes = upload_instance.question_paper.open().read()
#         ak_bytes = upload_instance.model_answer.open().read()
#         as_bytes = upload_instance.student_answers.open().read()
#     except Exception as e:
#         upload_instance.status = 'FAILED'
#         upload_instance.save()
#         return {'success': False, 'error': f"Error reading file: {e}"}

#     # 2. Define Prompt (Ensure this matches the expected format!)
#     prompt = """
# You are an experienced exam evaluator. Your task is to grade a student's answer sheet 
# (Student Answers) by comparing it against the official Model Answer and Question Paper.

# **INSTRUCTIONS:**
# 1.  **Strictly** analyze each question's answer in the Student Answers PDF against the Model Answer PDF.
# 2.  Provide a specific mark for each question based on correctness and completeness, and a brief reason for the score.
# 3.  Your FINAL output MUST contain ONLY two sections:
#     * Brief Summary
#     * Grading Result (JSON)

# **FORMAT:**
# === Brief Summary ===
# [Your paragraph summary here, e.g., "The student performed well on questions 1 and 3, but failed to attempt question 2."]

# === Grading Result (JSON) ===
# [
#     {
#         "question_no": 1, 
#         "marks": 5, 
#         "reason": "Correctly defined the term and provided relevant examples."
#     },
#     {
#         "question_no": 2, 
#         "marks": 0, 
#         "reason": "Not attempted, or answer was completely irrelevant."
#     }
# ]
#     """ # Note: You should paste your full prompt here.

#     # 3. Call Gemini API
#     try:
#         response = gemini_model.generate_content([
#             prompt,
#             {"mime_type": "application/pdf", "data": qp_bytes},
#             {"mime_type": "application/pdf", "data": ak_bytes},
#             {"mime_type": "application/pdf", "data": as_bytes}
#         ])
        
#         output_text = response.text.strip()
        
#         # 4. Extract JSON using Regex
#         json_match = re.search(r"=== Grading Result \(JSON\) ===\s*(\[.*?\])", output_text, re.DOTALL)
        
#         grading_result = []
#         if json_match:
#             grading_json_str = json_match.group(1).strip()
#             # Attempt to clean up and load the JSON
#             grading_result = json.loads(grading_json_str) 
        
#         # 5. Save results to the GradingResult model (CRITICAL)
#         GradingResult.objects.create(
#             upload=upload_instance,
#             result_json=grading_result,
#             full_gemini_response=output_text
#         )
        
#         # 6. Mark upload as graded (CRITICAL)
#         upload_instance.status = 'GRADED'
#         upload_instance.save()
        
#         return {'success': True}

#     except Exception as e:
#         # 7. Handle API or parsing failures
#         print(f"Gemini/Parsing Error for Upload {upload_instance.id}: {e}")
#         upload_instance.status = 'FAILED'
#         upload_instance.save()
#         return {'success': False, 'error': f"Grading failed: {e}"}

def extract_and_grade_with_gemini(upload_instance):
    gemini_model = configure_gemini()

    try:
        qp_bytes = upload_instance.question_paper.open().read()
        ak_bytes = upload_instance.model_answer.open().read()
        as_bytes = upload_instance.student_answers.open().read()
    except Exception as e:
        upload_instance.status = 'FAILED'
        upload_instance.save()
        return {'success': False, 'error': f"Error reading file: {e}"}

    prompt = prompt = """
You are an experienced exam evaluator. Your task is to grade a student's answer sheet 
(Student Answers) by comparing it against the official Model Answer and Question Paper.

**INSTRUCTIONS:**
1. Strictly analyze each question's answer in the Student Answers PDF against the Model Answer PDF.
2. For each question:
   - Award marks based on correctness and completeness.
   - Specify the **maximum marks possible** for that question.
   - Add a brief reason for the score.
3. Your FINAL output MUST contain ONLY two sections:
    * Brief Summary
    * Grading Result (JSON)

**FORMAT:**
=== Brief Summary ===
[Your short evaluation summary here]

=== Grading Result (JSON) ===
[
    {
        "question_no": 1, 
        "marks": 5, 
        "max_marks": 10,
        "reason": "Correctly defined the term and provided relevant examples."
    },
    {
        "question_no": 2, 
        "marks": 0, 
        "max_marks": 5,
        "reason": "Not attempted, or answer was completely irrelevant."
    }
]
"""


    try:
        response = gemini_model.generate_content([
            prompt,
            {"mime_type": "application/pdf", "data": qp_bytes},
            {"mime_type": "application/pdf", "data": ak_bytes},
            {"mime_type": "application/pdf", "data": as_bytes}
        ])
        
        output_text = response.text.strip()

        json_match = re.search(r"=== Grading Result \(JSON\) ===\s*(\[.*?\])", output_text, re.DOTALL)
        grading_result = json.loads(json_match.group(1).strip()) if json_match else []

        GradingResult.objects.create(
            upload=upload_instance,
            result_json=grading_result,
            full_gemini_response=output_text
        )

        upload_instance.status = 'GRADED'   # ✅ works now
        upload_instance.save()

        return {'success': True}

    except Exception as e:
        upload_instance.status = 'FAILED'   # ✅ works now
        upload_instance.save()
        return {'success': False, 'error': f"Grading failed: {e}"}



# ===============================================
# TEACHER APPLICATION VIEWS (Dashboard & Results)
# ===============================================

def upload_files(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.user = request.user   # ✅ attach logged-in teacher
            upload_instance.save()

            extract_and_grade_with_gemini(upload_instance)

            return JsonResponse({'status': 'success', 'redirect_url': '/teacher-results/'}, status=201)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    form = UploadForm()
    return render(request, 'teacher_dashboard.html', {'form': form})






def teacher_results_view(request):
    uploads = Upload.objects.filter(user=request.user).order_by('-uploaded_at').select_related('grading_result')

    context = {
        'all_uploads': uploads,
    }
    return render(request, 'teacher_results.html', context)




def detailed_grading_view(request, upload_id):
    """Displays the detailed JSON and full text output for a specific upload."""
    upload_instance = get_object_or_404(Upload, id=upload_id)

    # Retrieve the GradingResult for this specific Upload
    result = get_object_or_404(GradingResult, upload=upload_instance)

    context = {
        'upload': upload_instance,
        'grading_details': result.result_json,   # ✅ matches template
        'total_awarded': result.total_marks_awarded(),  # ✅ matches template
        'total_possible': result.total_possible_marks,  # ✅ matches template
    }
    return render(request, 'detailed_grading_result.html', context)
