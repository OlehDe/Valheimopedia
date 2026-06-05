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
# ДОПОМІЖНА ФУНКЦІЯ – ЗАВАНТАЖЕННЯ ВСІХ JSON-ФАЙЛІВ
# -----------------------------------------------------------------


def boss_detail_view(request, boss_token):
    """
    Детальна сторінка боса.
    Очікує токен боса (наприклад, '$item_boss_eikthyr').
    """
    all_data = load_all_items_data()
    bosses_list = all_data.get('Боси', [])
    boss = None
    for b in bosses_list:
        if b.get('token') == boss_token:
            boss = b
            break
    if not boss:
        error_message = f"Боса з токеном '{boss_token}' не знайдено."
    else:
        error_message = None
    return render(request, 'main_app/bosses_detail.html', {
        'boss': boss,
        'error': error_message
    })

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
        'biomes.json': 'Біоми',
        'building.json': 'Будівництво',
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

def building_detail_view(request, building_token):
    all_data = load_all_items_data()
    building_items = all_data.get('Будівництво', [])
    building = None
    for item in building_items:
        if item.get('token') == building_token:
            building = item
            break

    if not building:
        error_message = f"Будівельний елемент '{building_token}' не знайдено."
    else:
        error_message = None

    item_images = {}
    if building and building.get('crafted_items'):
        for crafted in building['crafted_items']:
            token = crafted.get('token')
            if token and token not in item_images:
                found_item = find_item_in_data(all_data, token)
                if found_item and found_item.get('image_url'):
                    item_images[token] = found_item['image_url']

    return render(request, 'main_app/building_detail.html', {
        'building': building,
        'error': error_message,
        'item_images': item_images,
    })

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Повертає значення словника за ключем або None, якщо ключ відсутній."""
    return dictionary.get(key)

def building_view(request):
    all_data = load_all_items_data()
    building_items = all_data.get('Будівництво', [])
    print("Кількість будівельних предметів:", len(building_items))  # для перевірки
    return render(request, 'main_app/building.html', {'building_items': building_items})

def biome_detail_view(request, biome_slug):
    all_data = load_all_items_data()
    biomes_list = all_data.get('Біоми', [])
    biome = None
    for b in biomes_list:
        if b.get('slug') == biome_slug:
            biome = b
            break
    if not biome:
        error_message = f"Біом '{biome_slug}' не знайдено."
    else:
        error_message = None
    return render(request, 'main_app/biome_detail.html', {
        'biome': biome,
        'error': error_message
    })
# -----------------------------------------------------------------
# ДОПОМІЖНА ФУНКЦІЯ – ЗАВАНТАЖЕННЯ ВСІХ JSON-ФАЙЛІВ


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
    Головна сторінка з інформацією про гру Valheim та біомами
    """
    # 1. Завантаження основної інформації про гру
    valheim_info_path = settings.BASE_DIR / 'data' / 'valheim_info.json'
    try:
        with open(valheim_info_path, 'r', encoding='utf-8') as f:
            valheim_info = json.load(f)
    except FileNotFoundError:
        valheim_info = {
            "title": "Про гру Valheim",
            "sections": [
                {
                    "title": "Ласкаво просимо до Valheimopedia!",
                    "type": "paragraph",
                    "content": "Тут ви знайдете всю необхідну інформацію про гру Valheim."
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

    # 2. Завантаження біомів з biomes.json
    biomes_path = settings.BASE_DIR / 'data' / 'biomes.json'
    biomes = []
    try:
        with open(biomes_path, 'r', encoding='utf-8') as f:
            biomes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        biomes = []

    # 3. Додаємо біоми до секції типу "grid" (або створюємо нову секцію)
    grid_section_found = False
    for section in valheim_info.get('sections', []):
        if section.get('type') == 'grid':
            # Замінюємо items біомами (з усіма полями: name, slug, image_url, description)
            section['items'] = biomes
            grid_section_found = True
            break

    # Якщо секції grid немає – створюємо її вручну
    if not grid_section_found and biomes:
        valheim_info.setdefault('sections', []).append({
            'title': 'Біоми світу Valheim',
            'type': 'grid',
            'items': biomes
        })

    # 4. Останні новини (якщо є модель)
    news_list = []  # поки що пустий

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