from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.signup, name="signup"),
]
