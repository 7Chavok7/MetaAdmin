from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    # Что показывать в списке
    list_display = [
        'full_name',
        'username',
        'birth_date',
        'hire_date',
        'is_active',
        'marital_status',
        'has_children',
    ]

    # Фильтры справа
    list_filter = [
        'is_active',
        'marital_status',
        'has_children',
        'hire_date',
        'birth_date',
    ]

    # Поиск
    search_fields = [
        'last_name',
        'first_name',
        'patronymic',
        'username',
        'registration_address',
        'residence_address',
    ]

    # Сортировка
    ordering = ['last_name', 'first_name']

    # Убираем лишние поля
    filter_horizontal = []

    # Группировка полей в форме
    fieldsets = (
        ('Учетные данные', {
            'fields': ('username', 'password', 'is_active', 'is_manager', 'is_staff', 'is_superuser')
        }),
        ('Личная информация', {
            'fields': ('last_name', 'first_name', 'patronymic', 'birth_date', 'photo')
        }),
        ('Адреса', {
            'fields': ('registration_address', 'residence_address')
        }),
        ('Семейное положение', {
            'fields': ('marital_status', 'has_children', 'children_count')
        }),
        ('Военная обязанность', {
            'fields': ('military_status',)
        }),
        ('Образование', {
            'fields': ('education_specialty', 'education_institution', 'education_year')
        }),
        ('Трудовой стаж', {
            'fields': ('previous_work_1', 'previous_work_2', 'previous_work_3')
        }),
        ('Даты', {
            'fields': ('hire_date', 'dismissal_date')
        }),
    )

    # Поля при создании нового сотрудника
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'last_name', 'first_name', 'hire_date'),
        }),
    )
