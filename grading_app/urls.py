from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path('about/', views.about, name='about'),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
]
