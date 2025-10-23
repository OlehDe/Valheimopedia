# main_app/apps.py
from django.apps import AppConfig

class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'
    label = 'main_app'  # Унікальна мітка