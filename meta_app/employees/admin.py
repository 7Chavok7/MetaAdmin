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
    # Заменяем username на login в list_display
    list_display = [
        'full_name',
        'login',  # ← заменил username
        'employee_id',
        'card_number',
        'birth_date',
        'hire_date',
        'is_active',
        'is_manager',
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
        'login',  # ← заменил username
        'employee_id',
        'card_number',
    ]
    ordering = ['last_name', 'first_name']
    filter_horizontal = []
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    inlines = [EmployeeSkillInline]

    # Убираем username из всех полей
    fieldsets = (
        ('Учетные данные', {
            'fields': ('login', 'employee_id', 'password', 'is_active', 'is_manager', 'is_staff', 'is_superuser')
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
        ('Аудит', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Убираем username из формы добавления
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'employee_id', 'password1', 'password2', 'last_name', 'first_name', 'hire_date'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj._created_by_user = request.user
        obj._updated_by_user = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_active=True, is_superuser=False)


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
    readonly_fields = ['certified_date']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser