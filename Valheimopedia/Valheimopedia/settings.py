"""
Django settings for Valheimopedia project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-occ66j-&fmvc$_my+gvd^nnw95j@-u@3a%j=(*0-mo_d0(yxw1'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'main_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Провайдери
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',   # GitHub тепер тут
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # вже є
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # обов'язково для allauth
]

ROOT_URLCONF = 'Valheimopedia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Valheimopedia.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise вже додано в MIDDLEWARE

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- НАЛАШТУВАННЯ ALLAUTH (оновлені) ----------
# Методи входу: дозволяємо email або username
ACCOUNT_LOGIN_METHODS = {'email', 'username'}   # замість ACCOUNT_AUTHENTICATION_METHOD

# Поля для реєстрації
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Email не підтверджуємо (для розробки)
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Вихід за GET запитом
ACCOUNT_LOGOUT_ON_GET = True

# Куди перенаправляти після входу
LOGIN_REDIRECT_URL = '/account/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# ---------- НАЛАШТУВАННЯ СОЦІАЛЬНИХ ПРОВАЙДЕРІВ ----------
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        # Без 'APPS' – дані клієнта будуть в адмінці
    },
    'github': {
        'SCOPE': ['user:email', 'read:user'],
        # Теж без APPS
    },
}

# Автоматичний sign-up через соціальні акаунти
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# Кастомний адаптер (якщо потрібен)
SOCIALACCOUNT_ADAPTER = 'main_app.adapters.CustomSocialAccountAdapter'

# Додатково: автентифікація за email (для сучасних версій allauth)
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True