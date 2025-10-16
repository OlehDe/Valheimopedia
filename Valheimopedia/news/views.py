from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core.checks import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm, UserLoginForm, AccountEditForm, NewsForm, CommentForm

from django.contrib.auth.decorators import login_required
from .models import News, Comment


def home(request):
    news_list = News.objects.all().order_by('-created_at')[:2]

    if request.method == 'POST':
        news_id = request.POST.get('news_id')
        news = get_object_or_404(News, id=news_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            return redirect('http://127.0.0.1:8000/')
    else:
        form = CommentForm()

    return render(request, 'news/home.html', {
        'news_list': news_list,
        'form': form,
    })

def news_list(request):
    news = News.objects.all().order_by('-created_date')
    return render(request, 'news/news_list.html', {'news': news})

@login_required
def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('http://127.0.0.1:8000/')
    else:
        form = NewsForm()

    return render(request, 'news/add_news.html', {'form': form})

def index(request):
    return render(request, "news/home.html")


def account_view(request):
    user_news = News.objects.filter(author=request.user).order_by('-created_at')

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('http://127.0.0.1:8000/')
    else:
        form = RegistrationForm()

    return render(request, 'news/account.html', {
        'form': form,
        'user': request.user,
        'news_list': user_news,
        'user_news': user_news,
    })

def account(request):
    return render(request, 'account.html')

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('http://127.0.0.1:8000/')
    else:
        form = RegistrationForm()

    return render(request, 'news/register.html', {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user =  authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('http://127.0.0.1:8000/')
    else:
        form = UserLoginForm()
    return render(request, 'news/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('http://127.0.0.1:8000/')


@login_required
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id, author=request.user)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            return redirect('http://127.0.0.1:8000/')
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/edit_news.html', {'form': form, 'news': news})

@login_required
def delete_news(request, news_id):
    news = get_object_or_404(News, id=news_id, author=request.user)
    if request.method == 'POST':
        news.delete()
        return redirect('/')
    return render(request, 'news/delete_confirm.html', {'news': news})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    comment.delete()
    return redirect('http://127.0.0.1:8000/comments/10/')

@login_required
def user_comments(request):
    comments = Comment.objects.filter(author=request.user)
    return render(request, 'news/user_comments.html', {'comments': comments})

def news_comments(request, news_id):
    news = get_object_or_404(News, id=news_id)
    comments = news.comments.all()
    return render(request, 'news/comments.html', {'news': news, 'comments': comments})

@login_required
def add_comment(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            return redirect('news:news_comments', news_id=news.id)
    return redirect('news:news_comments', news_id=news.id)

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news/news_detail.html', {'news': news})

from django.contrib.auth.models import User

def user_news(request, username):
    author = get_object_or_404(User, username=username)
    news_list = News.objects.filter(author=author).order_by('-created_at')
    return render(request, 'news/user_news.html', {
        'author': author,
        'news_list': news_list,
        'current_user': request.user
    })

def all_news(request):
    news_list = News.objects.all().order_by('-created_at')
    context = {'news_list': news_list}
    return render(request, 'news/all_news.html', context)