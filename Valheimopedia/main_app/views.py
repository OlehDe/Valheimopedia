# main_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserLoginForm
from .models import Comment

def home(request):
    return render(request, 'main_app/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main_app:home')
    else:
        form = RegistrationForm()
    return render(request, 'main_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('main_app:home')
    else:
        form = UserLoginForm()
    return render(request, 'main_app/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('main_app:home')

@login_required
def account_view(request):
    user_comments = Comment.objects.filter(author=request.user)
    return render(request, 'main_app/account.html', {
        'user_comments': user_comments
    })

@login_required
def user_comments(request):
    comments = Comment.objects.filter(author=request.user)
    return render(request, 'main_app/user_comments.html', {'comments': comments})

@login_required
def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)
    if comment.author == request.user or request.user.is_staff:
        comment.delete()
    return redirect('main_app:user_comments')