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
# ФУНКЦІЯ ДЛЯ ВІДОБРАЖЕННЯ ВСІХ ПРЕДМЕТІВ (НЕ ЗМІНЮВАЛАСЬ)
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


# -----------------------------------------------------------------
# ВИПРАВЛЕНА ФУНКЦІЯ ДЛЯ ДЕТАЛЕЙ ПРЕДМЕТА (ТЕПЕР ВИКОРИСТОВУЄ find_item_in_data
# ДЛЯ ЗНАХОДЖЕННЯ ЯК САМОГО ПРЕДМЕТА, ТАК І ЙОГО МАТЕРІАЛІВ)
# -----------------------------------------------------------------
def item_detail_view(request, item_asset_id):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_item = None
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_categories = data.get('items', {})

            # 1. Знаходимо сам предмет за assetId або token
            found_item = find_item_in_data(all_categories, item_asset_id)

            if found_item:
                crafting_stats = found_item.get('stats', {}).get('crafting', {})
                material_ids = crafting_stats.get('materials')

                # Якщо materials - це список ID, збагачуємо його
                if isinstance(material_ids, list):
                    enriched_materials = []

                    for identifier in material_ids:
                        if isinstance(identifier, str):
                            # Знаходимо повний об'єкт матеріалу за ID або Токеном
                            material_data = find_item_in_data(all_categories, identifier)

                            if material_data:
                                # !!! ЗВЕРНІТЬ УВАГУ: КІЛЬКІСТЬ (quantity) ТУТ ВСЕ ЩЕ ЗАГЛУШКА !!!
                                # Щоб отримати реальну кількість, вам потрібно знайти її у вашій JSON-структурі
                                # і зіставити з 'identifier'
                                quantity_value = 'Знайдено'

                                enriched_materials.append({
                                    'name': material_data.get('name', 'N/A'),
                                    'token': material_data.get('token', ''),
                                    'assetId': material_data.get('assetId', ''),
                                    'quantity': quantity_value
                                })
                            else:
                                # Якщо матеріал не знайдено (наприклад, ID є, а предмета немає)
                                enriched_materials.append(
                                    {'assetId': identifier, 'name': f"Не знайдено ({identifier})", 'quantity': 'N/A'})

                        else:
                            # Якщо елемент не рядок (можливо, це вже об'єкт)
                            enriched_materials.append(identifier)

                    crafting_stats['materials'] = enriched_materials
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
# РЕШТА ФУНКЦІЙ (НЕ ЗМІНЮВАЛИСЬ)
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