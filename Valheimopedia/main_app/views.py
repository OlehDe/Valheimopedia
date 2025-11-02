# main_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Припускаємо, що ці файли існують у вашому додатку
from .forms import RegistrationForm, UserLoginForm
from .models import Comment

import json
from django.conf import settings


# main_app/views.py
# ... (всі ваші import-и та інші функції) ...

# 🔽======================================
# 🔽 ФУНКЦІЯ ДЛЯ ВІДОБРАЖЕННЯ JSON (ВИПРАВЛЕНО)
# 🔽======================================

def all_items_view(request):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    items_data = {}  # За замовчуванням - порожній словник
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 🔽🔽🔽 ОСЬ ЦЕЙ РЯДОК ПОТРІБНО ЗМІНИТИ 🔽🔽🔽
            items_data = data.get('items', {})  # Беремо тільки об'єкт "items"
            # 🔼🔼🔼 КІНЕЦЬ ВИПРАВЛЕННЯ 🔼🔼🔼

    except FileNotFoundError:
        error_message = f"Помилка: Файл не знайдено за шляхом {file_path}. Переконайтеся, що він існує."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений або має невірний формат JSON."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    # Передаємо дані та можливу помилку у шаблон
    return render(request, 'main_app/all_items.html', {
        'items': items_data,
        'error': error_message
    })


# -----------------------------------------------------------------
# 🔽 ФУНКЦІЯ ДЛЯ ДЕТАЛЕЙ ПРЕДМЕТА (ВИПРАВЛЕНО) 🔽
# -----------------------------------------------------------------

# Нова рекурсивна функція пошуку
def find_item_in_data(data, asset_id):
    if isinstance(data, dict):
        if data.get('assetId') == asset_id:
            return data
        for key, value in data.items():
            found = find_item_in_data(value, asset_id)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_item_in_data(item, asset_id)
            if found:
                return found
    return None


def item_detail_view(request, item_asset_id):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_item = None
    error_message = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_categories = data.get('items', {})  # Починаємо пошук з "items"

            # Використовуємо рекурсивну функцію
            found_item = find_item_in_data(all_categories, item_asset_id)

        if not found_item:
            error_message = "Предмет з таким ID не знайдено."

    except FileNotFoundError:
        error_message = "Помилка: Файл 'items.json' не знайдено."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    return render(request, 'main_app/item_detail.html', {
        'item': found_item,
        'error': error_message
    })


# -----------------------------------------------------------------
# 🔽 ФУНКЦІЯ ДЛЯ КОМПЛЕКТІВ (БЕЗ ЗМІН, ВОНА ПРАЦЮЄ) 🔽
# -----------------------------------------------------------------
def set_detail_view(request, set_slug):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_set = None
    error_message = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sets_list = data.get('items', {}).get('Комплект обладунків', [])

            for armor_set in sets_list:
                if armor_set.get('setSlug') == set_slug:
                    found_set = armor_set
                    break

    except FileNotFoundError:
        error_message = "Помилка: Файл 'items.json' не знайдено."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    if not found_set:
        error_message = "Комплект броні з таким ID не знайдено."

    return render(request, 'main_app/set_detail.html', {
        'set': found_set,
        'error': error_message
    })


# ... (решта ваших функцій: home, register, login і т.д.) ...


def home(request):
    # return render(request, 'main_app/home.html')
    # Тимчасово перенаправляємо на сторінку предметів
    return redirect('main_app:all_items')


# (Тут ваші функції register_view, login_view, logout_view і т.д.)
# ...
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main_app:home')
        else:
            return render(request, 'main_app/register.html', {'form': form})
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