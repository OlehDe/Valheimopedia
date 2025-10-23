# main_app/urls.py
from django.urls import path
from . import views  # Використовуйте відносний імпорт
from .views import register_view, login_view  # Використовуйте відносний імпорт

app_name = "main_app"

urlpatterns = [
    path('', views.home, name='home'),
    path('account/', views.account_view, name='account'),
    path('logout/', views.logout_view, name='logout'),
    path('user_comments/', views.user_comments, name='user_comments'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]