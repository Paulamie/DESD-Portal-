from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required

def homepage(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect logged-in users to home
    return render(request, 'student_management/index.html')

@login_required
def home(request):
    return render(request, 'student_management/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home after registration
    else:
        form = UserRegisterForm()
    return render(request, 'student_management/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after login
        else:
            return render(request, 'student_management/login.html', {'error': 'Invalid email or password'})
    return render(request, 'student_management/login.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')
