from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Розбиває рядок за заданим аргументом."""
    if value and isinstance(value, str):
        return value.split(arg)
    return [value] if value is not None else []

@register.filter(name='get_item')
def get_item(value, key):
    """Отримує елемент за індексом зі списку або за ключем зі словника."""
    try:
        return value[key]
    except (TypeError, IndexError, KeyError):
        return ''

@register.filter(name='strip')
def strip_filter(value):
    """Видаляє пробіли з обох кінців рядка."""
    if value and isinstance(value, str):
        return value.strip()
    return value