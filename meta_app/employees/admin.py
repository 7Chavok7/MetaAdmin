from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from .models import Employee, Skill, EmployeeSkill


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1
    fields = ['skill', 'level', 'note']
    autocomplete_fields = ['skill']


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = [
        'full_name',
        'username',
        'birth_date',
        'hire_date',
        'is_active',
        'is_manager',
        'marital_status',
        'has_children',
    ]
    list_filter = [
        'is_active',
        'is_manager',
        'marital_status',
        'has_children',
        'hire_date',
    ]
    search_fields = [
        'last_name',
        'first_name',
        'patronymic',
        'username',
    ]
    ordering = ['last_name', 'first_name']
    filter_horizontal = []

    inlines = [EmployeeSkillInline]

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

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'last_name', 'first_name', 'hire_date'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Если пользователь не суперпользователь - делаем поля только для чтения"""
        if not request.user.is_superuser:
            # Все поля только для чтения
            return [f.name for f in self.model._meta.fields]
        return []

    def has_add_permission(self, request):
        """Разрешаем добавление только суперпользователям"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление только суперпользователям"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Разрешаем изменение только суперпользователям"""
        return request.user.is_superuser

    def get_queryset(self, request):
        """Ограничиваем список сотрудников для не-суперпользователей"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Обычные пользователи видят только активных сотрудников
        return qs.filter(is_active=True)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ['employee', 'skill', 'level', 'certified_date']
    list_filter = ['skill__category', 'level']
    search_fields = ['employee__full_name', 'skill__name']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


# Убираем группы из админки для обычных пользователей
admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
