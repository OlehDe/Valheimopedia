from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import News, Comment
from .forms import NewsForm, CommentForm
from django.contrib.auth.decorators import login_required

def home(request):
    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'news/home.html', {'news_list': news_list})

def news_detail(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    comments = news.comments.all()
    return render(request, 'news/detail.html', {'news': news, 'comments': comments})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'news/register.html', {'form': form})

@login_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('home')
    else:
        form = NewsForm()
    return render(request, 'news/create_news.html', {'form': form})

@login_required
def edit_news(request, news_id):
    news = get_object_or_404(News, pk=news_id, author=request.user)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            return redirect('news_detail', news_id=news.id)
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/edit_news.html', {'form': form})

@login_required
def delete_news(request, news_id):
    news = get_object_or_404(News, pk=news_id, author=request.user)
    if request.method == 'POST':
        news.delete()
        return redirect('home')
    return render(request, 'news/delete_news.html', {'news': news})

@login_required
def add_comment(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.news = news
            comment.save()
            return redirect('news_detail', news_id=news.id)
    else:
        form = CommentForm()
    return render(request, 'news/add_comment.html', {'form': form})
