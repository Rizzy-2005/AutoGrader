from django.urls import path
from . import views

urlpatterns = [
    # General Routes
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path('about/', views.about, name='about'),
    path('logout/',views.logout,name="logout"),
    
    # Student Dashboard
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    
    # 🌟 Teacher Routes 🌟
    path("teacher-dashboard/", views.upload_files, name="teacher_dashboard"), 
    path('teacher-results/', views.teacher_results_view, name='teacher_results'),
    
    # Detailed Grading (points to the correct function in views.py)
    path('results/<int:upload_id>/details/', views.detailed_grading_view, name='detailed_grading'),
]
