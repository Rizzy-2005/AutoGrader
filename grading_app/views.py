from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def landing(request):
    return render(request, "landing.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")  # later redirect to dashboard
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        User.objects.create_user(username=username, email=email, password=password)
        return redirect("/login/")
    return render(request, "signup.html")
