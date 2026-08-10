from django import template
from decimal import Decimal


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


@register.filter(name='sum_values')
def sum_values(salaries):
    """Суммирует все зарплаты в массиве за год"""
    if not salaries:
        return 0
    
    total = Decimal('0')
    for salary in salaries:
        if salary and salary.get('is_calculated'):
            total += Decimal(str(salary.get('total', 0)))
    
    return total


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
def add(value, arg):
    """Сложение"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value