# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserLoginForm
from .models import Comment

import json
from django.conf import settings
from pathlib import Path


# -----------------------------------------------------------------
# ДОПОМІЖНА ФУНКЦІЯ – ЗАВАНТАЖЕННЯ ВСІХ JSON-ФАЙЛІВ
# -----------------------------------------------------------------
def load_all_items_data():
    """
    Завантажує всі JSON-файли з папки data/ і повертає словник,
    де ключі – назви категорій (українською), значення – їхній вміст.
    """
    data_folder = settings.BASE_DIR / 'data'
    file_to_key = {
        'weapons.json': 'Зброя',
        'armor_sets.json': 'Комплект обладунків',
        'armor_pieces.json': 'Обладунки',
        'tools.json': 'Інструменти',
        'consumables.json': 'Витратні матеріали',
        'materials.json': 'Матеріали',
        'trophies.json': 'Trophy',
        'misc.json': 'Misc',
        'unique_items.json': 'Унікальні предмети',
        'customization.json': 'Customization',
        'bosses.json': 'Боси',
    }
    combined = {}
    for filename, key in file_to_key.items():
        file_path = data_folder / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                combined[key] = json.load(f)
        except FileNotFoundError:
            # Якщо файлу немає – просто пропускаємо (або можна кинути помилку)
            combined[key] = {}
        except json.JSONDecodeError:
            combined[key] = {}
    return combined


# -----------------------------------------------------------------
# РЕКУРСИВНИЙ ПОШУК ПРЕДМЕТА ЗА ТОКЕНОМ (АБО assetId)
# -----------------------------------------------------------------
def find_item_in_data(data, identifier):
    """
    Шукає предмет за 'token' або 'assetId' (якщо останній ще десь присутній).
    Повертає знайдений словник або None.
    """
    if isinstance(data, dict):
        # Перевіряємо чи сам словник є шуканим предметом
        if data.get('token') == identifier or data.get('assetId') == identifier:
            return data
        # Рекурсивно обходимо всі значення
        for value in data.values():
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
# ГОЛОВНА СТОРІНКА З УСІМА ПРЕДМЕТАМИ
# -----------------------------------------------------------------
def all_items_view(request):
    items_data = {}
    error_message = None
    try:
        items_data = load_all_items_data()
    except Exception as e:
        error_message = f"Помилка завантаження даних: {e}"

    return render(request, 'main_app/all_items.html', {
        'items': items_data,
        'error': error_message
    })


# -----------------------------------------------------------------
# ДЕТАЛЬНА СТОРІНКА ПРЕДМЕТА (ЗА ТОКЕНОМ)
# -----------------------------------------------------------------
def item_detail_view(request, item_token):
    """
    Очікує, що в URL передається токен предмета (наприклад, '$item_helmet_padded').
    """
    all_data = load_all_items_data()
    found_item = None
    error_message = None
    total_materials_list = []

    try:
        # Шукаємо предмет за токеном у всіх категоріях
        found_item = find_item_in_data(all_data, item_token)

        if found_item:
            # Обробка матеріалів для крафту (аналогічно до попередньої логіки)
            crafting_stats = found_item.get('stats', {}).get('crafting', {})
            material_ids = crafting_stats.get('materials')          # список токенів або assetId
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
                        material_data = find_item_in_data(all_data, identifier)
                        quantity_list = quantities.get(identifier, [])
                        quantity_needed = int(quantity_list[i]) if i < len(quantity_list) else 0

                        if quantity_needed > 0:
                            material_name = material_data.get('name', f"Невідомий матеріал ({identifier})") if material_data else f"Невідомий матеріал ({identifier})"

                            required_materials_for_level.append({
                                'name': material_name,
                                'quantity': quantity_needed,
                                'token': material_data.get('token', '') if material_data else identifier,
                                'assetId': material_data.get('assetId', '') if material_data else identifier,
                                'image_url': material_data.get('image_url', '') if material_data else ''
                            })

                    if required_materials_for_level or level == 1:
                        level_requirements.append({
                            'level': level,
                            'is_craft': (level == 1),
                            'materials': required_materials_for_level
                        })

            found_item['level_requirements'] = level_requirements

            # Підрахунок загальної кількості матеріалів на всі рівні
            total_map = {}
            for req in level_requirements:
                for mat in req.get('materials', []):
                    key = mat.get('token') or mat.get('assetId') or mat['name']
                    if key not in total_map:
                        total_map[key] = {
                            'name': mat['name'],
                            'quantity': 0,
                            'image_url': mat.get('image_url'),
                            'token': mat.get('token'),
                            'assetId': mat.get('assetId')
                        }
                    total_map[key]['quantity'] += mat['quantity']
            total_materials_list = list(total_map.values())

        else:
            error_message = f"Предмет з токеном '{item_token}' не знайдено."

    except Exception as e:
        error_message = f"Помилка при обробці даних: {e}"

    return render(request, 'main_app/item_detail.html', {
        'item': found_item,
        'error': error_message,
        'total_materials': total_materials_list
    })


# -----------------------------------------------------------------
# ДЕТАЛЬНА СТОРІНКА КОМПЛЕКТУ БРОНІ (ЗА setSlug)
# -----------------------------------------------------------------
def set_detail_view(request, set_slug):
    all_data = load_all_items_data()
    found_set = None
    error_message = None

    try:
        sets_list = all_data.get('Комплект обладунків', [])
        for armor_set in sets_list:
            if armor_set.get('setSlug') == set_slug:
                found_set = armor_set
                # Завантажуємо повні дані кожного предмета з комплекту за токеном
                items_with_data = []
                for token in found_set.get('items', []):
                    item_data = find_item_in_data(all_data, token)
                    if item_data:
                        items_with_data.append(item_data)
                found_set['items_with_data'] = items_with_data
                break

        if not found_set:
            error_message = f"Комплект броні '{set_slug}' не знайдено."

    except Exception as e:
        error_message = f"Помилка при завантаженні даних: {e}"

    return render(request, 'main_app/set_detail.html', {
        'set': found_set,
        'error': error_message
    })


# -----------------------------------------------------------------
# РЕШТА ФУНКЦІЙ (НЕ ЗМІНЮВАЛИСЬ)
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# ГОЛОВНА СТОРІНКА З ІНФОРМАЦІЄЮ ПРО ГРУ
# -----------------------------------------------------------------
def home(request):
    """
    Головна сторінка з інформацією про гру Valheim
    """
    # Завантаження даних про гру з JSON файлу
    valheim_info_path = settings.BASE_DIR / 'data' / 'valheim_info.json'

    try:
        with open(valheim_info_path, 'r', encoding='utf-8') as f:
            valheim_info = json.load(f)
    except FileNotFoundError:
        # Якщо файл не знайдено, створюємо базову структуру
        valheim_info = {
            "title": "Про гру Valheim",
            "sections": [
                {
                    "title": "Ласкаво просимо до Valheimopedia!",
                    "type": "paragraph",
                    "content": "Тут ви знайдете всю необхідну інформацію про гру Valheim: предмети, рецепти, босів, біоми та багато іншого."
                }
            ]
        }
    except json.JSONDecodeError:
        valheim_info = {
            "title": "Помилка завантаження",
            "sections": [
                {
                    "title": "Помилка",
                    "type": "paragraph",
                    "content": "Не вдалося завантажити інформацію про гру. Спробуйте пізніше."
                }
            ]
        }

    # Отримання останніх новин (якщо у вас є модель News)
    # news_list = News.objects.all().order_by('-created_at')[:5]
    news_list = []  # Поки що пустий список

    return render(request, 'main_app/home.html', {
        'valheim_info': valheim_info,
        'news_list': news_list
    })


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