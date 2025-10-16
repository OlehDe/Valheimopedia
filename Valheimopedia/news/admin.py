from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import News, Comment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Активувати обрані облікові записи"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Деактивувати обрані облікові записи"

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'comment_count')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author')
        }),
        ('Додатково', {
            'fields': ('image', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Коментарі'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'news', 'created_at')
    list_filter = ('created_at', 'author', 'news')
    search_fields = ('content', 'author__username', 'news__title')
    raw_id_fields = ('author', 'news')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

# Перереєструємо стандартну модель User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)