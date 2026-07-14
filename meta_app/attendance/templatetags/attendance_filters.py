from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    if dictionary is None:
        return None
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None


@register.filter(name='get_actual_hours')
def get_actual_hours(attendance):
    """Получить фактические часы из записи"""
    if attendance is None:
        return 0
    return attendance.actual_hours


@register.filter
def get_month_name(month):
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return months[month - 1] if 1 <= month <= 12 else ''


@register.filter
def sum_hours(data):
    return sum([item['total_hours'] for item in data])


@register.filter
def sum_overtime(data):
    return sum([item['overtime'] for item in data])


@register.filter
def sum_weekend(data):
    return sum([item['weekend_works'] for item in data])


@register.filter
def split(value, arg):
    if not value:
        return []
    return [item.strip() for item in value.split(arg)]


@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def add(value, arg):
    """Сложение"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value
