# Valheimopedia/urls.py (Головний файл проєкту)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # <-- Додайте цей імпорт
from django.conf.urls.static import static  # <-- Додайте цей імпорт

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),  # Тут підключена ваша програма
    # ... інші шляхи
]

# 👇 ЦЕЙ БЛОК ВИПРАВИТЬ 404 ПОМИЛКИ ДЛЯ СТИЛІВ ТА СКРИПТІВ

if settings.DEBUG:
    # Обслуговування статичних файлів (CSS, JS) у режимі розробки
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Рекомендовано також додати медіа-файли
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)