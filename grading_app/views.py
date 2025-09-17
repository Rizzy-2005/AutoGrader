
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

User = get_user_model()
def landing(request):
    return render(request, "landing.html")

# def user_login(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         password = request.POST["password"]
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect("/")  # later redirect to dashboard
#     return render(request, "login.html")

# def signup(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]
#         password = request.POST["password"]
#         User.objects.create_user(username=username, email=email, password=password)
#         return redirect("/login/")
#     return render(request, "signup.html")

def about(request):
    return render(request, "about.html")


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

User = get_user_model()

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]  # from dropdown

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.user_type = role  # <-- Save the role
        user.save()

        return redirect("login")

    return render(request, "signup.html")

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


def student_dashboard(request):
    return render(request, "student_dashboard.html")


def teacher_dashboard(request):
    return render(request, "teacher_dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")
