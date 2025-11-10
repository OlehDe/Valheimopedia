# main_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserLoginForm
from .models import Comment

import json
from django.conf import settings


# -----------------------------------------------------------------
# ФУНКЦІЯ ДЛЯ ВІДОБРАЖЕННЯ ВСІХ ПРЕДМЕТІВ
# -----------------------------------------------------------------
def all_items_view(request):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    items_data = {}
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items_data = data.get('items', {})
    except FileNotFoundError:
        error_message = f"Помилка: Файл не знайдено за шляхом {file_path}. Переконайтеся, що він існує."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений або має невірний формат JSON."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    return render(request, 'main_app/all_items.html', {
        'items': items_data,
        'error': error_message
    })


# -----------------------------------------------------------------
# 🚀 ВИПРАВЛЕНА РЕКУРСИВНА ФУНКЦІЯ ПОШУКУ (ШУКАЄ ЗА ID АБО ТОКЕНОМ) 🚀
# -----------------------------------------------------------------
def find_item_in_data(data, identifier):
    """Шукає предмет за 'assetId' або 'token'."""
    if isinstance(data, dict):
        # Шукаємо збіг за assetId або token
        if data.get('assetId') == identifier or data.get('token') == identifier:
            return data
        for key, value in data.items():
            found = find_item_in_data(value, identifier)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_item_in_data(item, identifier)
            if found:
                return found
    return None


def find_item_in_data(data, identifier):
    """Шукає предмет за 'assetId' або 'token'."""
    if isinstance(data, dict):
        if data.get('assetId') == identifier or data.get('token') == identifier:
            return data
        for key, value in data.items():
            found = find_item_in_data(value, identifier)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_item_in_data(item, identifier)
            if found:
                return found
    return None


# -----------------------------------------------------------------
# 🚀 ВИПРАВЛЕНА ФУНКЦІЯ ДЛЯ ДЕТАЛЕЙ ПРЕДМЕТА (З ФОТО МАТЕРІАЛІВ) 🚀
# -----------------------------------------------------------------
def item_detail_view(request, item_asset_id):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_item = None
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_categories = data.get('items', {})

            found_item = find_item_in_data(all_categories, item_asset_id)

            if found_item:
                crafting_stats = found_item.get('stats', {}).get('crafting', {})
                material_ids = crafting_stats.get('materials')
                quantities = crafting_stats.get('material_quantities', {})

                level_requirements = []

                if material_ids and quantities:

                    max_levels = 0
                    for q_list in quantities.values():
                        max_levels = max(max_levels, len(q_list))

                    for i in range(max_levels):
                        level = i + 1
                        required_materials_for_level = []

                        for identifier in material_ids:
                            material_data = find_item_in_data(all_categories, identifier)

                            quantity_list = quantities.get(identifier, [])
                            quantity_needed = int(quantity_list[i]) if i < len(quantity_list) else 0

                            if quantity_needed > 0:
                                material_name = material_data.get('name',
                                                                  f"Не знайдено ({identifier})") if material_data else f"Не знайдено ({identifier})"

                                required_materials_for_level.append({
                                    'name': material_name,
                                    'quantity': quantity_needed,
                                    'token': material_data.get('token', '') if material_data else identifier,
                                    'assetId': material_data.get('assetId', '') if material_data else identifier,
                                    # 🚀 ДОДАЄМО URL ЗОБРАЖЕННЯ 🚀
                                    'image_url': material_data.get('image_url', '') if material_data else ''
                                })

                        if required_materials_for_level or level == 1:
                            level_requirements.append({
                                'level': level,
                                'is_craft': (level == 1),
                                'materials': required_materials_for_level
                            })

                found_item['level_requirements'] = level_requirements
            else:
                error_message = "Предмет з таким ID або токеном не знайдено."

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
# ... (set_detail_view та інші функції - БЕЗ ЗМІН) ...
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# ФУНКЦІЯ ДЛЯ КОМПЛЕКТІВ (НЕ ЗМІНЮВАЛАСЬ)
# -----------------------------------------------------------------
def set_detail_view(request, set_slug):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_set = None
    error_message = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_categories = data.get('items', {})
            sets_list = data.get('items', {}).get('Комплект обладунків', [])

            for armor_set in sets_list:
                if armor_set.get('setSlug') == set_slug:
                    found_set = armor_set

                    items_with_data = []
                    for asset_id in found_set.get('items', []):
                        item_data = find_item_in_data(all_categories, asset_id)
                        if item_data:
                            items_with_data.append(item_data)

                    found_set['items_with_data'] = items_with_data
                    break

    except FileNotFoundError:
        error_message = "Помилка: Файл 'items.json' не знайдено."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    if not found_set:
        error_message = f"Комплект броні '{set_slug}' не знайдено."

    return render(request, 'main_app/set_detail.html', {
        'set': found_set,
        'error': error_message
    })


# -----------------------------------------------------------------
# РЕШТА ФУНКЦІЙ
# -----------------------------------------------------------------

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