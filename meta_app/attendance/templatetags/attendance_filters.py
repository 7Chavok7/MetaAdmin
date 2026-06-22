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
