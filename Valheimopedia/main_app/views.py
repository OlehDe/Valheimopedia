# main_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserLoginForm
from .models import Comment

# 🔽 Нові імпорти для роботи з JSON та шляхами
import json
from django.conf import settings


# 🔼 Кінець нових імпортів

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
            # ⬇️ Якщо є помилки — просто показуємо цю ж сторінку з ними
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


# 🔽======================================
# 🔽 Нова функція для відображення JSON
# 🔽======================================

def all_items_view(request):
    # Будуємо шлях до файлу.
    # Це припускає, що папка 'data' лежить у корені вашого проєкту (поряд з manage.py)
    file_path = settings.BASE_DIR / 'data' / 'items.json'

    items_data = []  # Список за замовчуванням
    error_message = None  # Для відображення помилки

    try:
        # Відкриваємо файл і завантажуємо дані
        with open(file_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)

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

# 🔽======================================
# 🔽 НОВА ФУНКЦІЯ ДЛЯ ДЕТАЛЕЙ ПРЕДМЕТА
# 🔽======================================
def item_detail_view(request, item_asset_id):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_item = None
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_categories_data = data.get('items', {})

            # Починаємо пошук предмета
            # Ця логіка складна, бо у вас вкладені категорії
            for category_key, category_value in all_categories_data.items():

                if isinstance(category_value, list):
                    # Для простих категорій (напр. "ОдноручнаЗброя": [...])
                    for item in category_value:
                        if item.get('assetId') == item_asset_id:
                            found_item = item
                            break

                elif isinstance(category_value, dict):
                    # Для вкладених категорій (напр. "Обладунки": { "Шолом": [...] })
                    for sub_key, sub_list in category_value.items():
                        if isinstance(sub_list, list):
                            for item in sub_list:
                                if item.get('assetId') == item_asset_id:
                                    found_item = item
                                    break
                        if found_item: break

                if found_item: break

    except FileNotFoundError:
        error_message = "Помилка: Файл 'items.json' не знайдено."
    except json.JSONDecodeError:
        error_message = "Помилка: Файл 'items.json' пошкоджений."
    except Exception as e:
        error_message = f"Виникла неочікувана помилка: {e}"

    # Якщо предмет не знайдено після всіх циклів
    if not found_item and not error_message:
        error_message = "Предмет з таким ID не знайдено."

    return render(request, 'main_app/item_detail.html', {
        'item': found_item,
        'error': error_message
    })


# ... (всі ваші існуючі import-и та view-функції) ...

# 🔽======================================
# 🔽 НОВА ФУНКЦІЯ ДЛЯ ДЕТАЛЕЙ КОМПЛЕКТУ
# 🔽======================================
def set_detail_view(request, set_slug):
    file_path = settings.BASE_DIR / 'data' / 'items.json'
    found_set = None
    error_message = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Отримуємо список комплектів
            sets_list = data.get('items', {}).get('Комплект обладунків', [])

            # Шукаємо потрібний комплект за 'setSlug'
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

    # Якщо комплект не знайдено
    if not found_set and not error_message:
        error_message = "Комплект броні з таким ID не знайдено."

    return render(request, 'main_app/set_detail.html', {
        'set': found_set,
        'error': error_message
    })