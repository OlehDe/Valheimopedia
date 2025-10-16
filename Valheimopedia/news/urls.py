from django.urls import path

from . import views

from .views import register_view, login_view


app_name = "news"

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news_list, name='news_list'),
    path('add_news/', views.add_news, name='add_news'),
    path('account', views.account_view, name='account'),
    path('logout', views.logout_view, name='logout'),
    path('user_comments/', views.user_comments, name='user_comments'),
    path('all_news/', views.all_news, name='all_news'),

    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),

    path('user_news/<str:username>/', views.user_news, name='user_news'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('comments/<int:news_id>/', views.news_comments, name='news_comments'),
    path('edit_news/<int:news_id>', views.edit_news, name='edit_news'),
    path('delete_news/<int:news_id>', views.delete_news, name='delete_news'),
    path('news_detail/<int:news_id>/', views.news_detail, name='news_detail'),
    path('comments/<int:news_id>/add/', views.add_comment, name='add_comment'),
]

