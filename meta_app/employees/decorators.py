# meta_app/employees/decorators.py

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def is_manager(user):
    """Проверка, является ли пользователь менеджером (включая директора и замов)"""
    if not user.is_authenticated:
        return False
    if hasattr(user, 'role'):
        return user.role in ['manager', 'director', 'deputy']
    return user.is_manager  # fallback


def is_director(user):
    """Проверка, является ли пользователь директором"""
    if not user.is_authenticated:
        return False
    if hasattr(user, 'role'):
        return user.role == 'director'
    return user.is_superuser  # fallback


def is_deputy(user):
    """Проверка, является ли пользователь заместителем"""
    if not user.is_authenticated:
        return False
    if hasattr(user, 'role'):
        return user.role == 'deputy'
    return False


def director_required(view_func):
    """Декоратор для доступа только директора"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        if not is_director(request.user):
            messages.error(request, 'Доступ запрещён. Только для директора.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_or_director_required(view_func):
    """Декоратор для доступа менеджеров, замов и директора"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        if not is_manager(request.user):
            messages.error(request, 'Доступ запрещён. Только для руководителей.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def deputy_or_director_required(view_func):
    """Декоратор для доступа замов и директора"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        if not is_director(request.user) and not is_deputy(request.user):
            messages.error(request, 'Доступ запрещён. Только для руководства.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper