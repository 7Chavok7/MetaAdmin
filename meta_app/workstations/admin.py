from django.contrib import admin
from .models import Workstation, EmployeeWorkstation, Department


class EmployeeWorkstationInline(admin.TabularInline):
    model = EmployeeWorkstation
    extra = 1
    fields = [
        'workstation', 
        'is_primary', 
        'assigned_date', 
        'note'
    ]
    autocomplete_fields = [
        'workstation'
    ]


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'short_name', 
        'department',
        'schedule_type',
        'work_start', 
        'work_end', 
        'hours_per_day', 
        'is_active'
    ]
    list_filter = [
        'department',
        'schedule_type', 
        'is_active'
    ]
    search_fields = [
        'name', 
        'short_name',
        'department__name'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'created_by', 
        'updated_by'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name', 
                'short_name', 
                'department', 
                'color', 
                'is_active'
            )
        }),
        ('Режим работы', {
            'fields': (
                'schedule_type', 
                'work_start', 
                'work_end', 
                'hours_per_day'
            )
        }),
        ('Аудит', {
            'fields': (
                'created_by', 
                'created_at', 
                'updated_by', 
                'updated_at'
            ),
            'classes': (
                'collapse',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmployeeWorkstation)
class EmployeeWorkstationAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 
        'workstation', 
        'is_primary', 
        'assigned_date'
    ]
    list_filter = [
        'workstation', 
        'is_primary'
    ]
    search_fields = [
        'employee__full_name', 
        'workstation__name'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'created_by', 
        'updated_by'
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'code', 
        'parent', 
        'is_active', 
        'order'
    ]
    list_filter = [
        'is_active', 
        'parent'
    ]
    search_fields = [
        'name', 
        'code'
    ]
    ordering = [
        'order', 
        'name'
    ]
    
    fieldsets = (
        ('Основное', {
            'fields': (
                'name', 
                'code', 
                'parent', 
                'description'
            )
        }),
        ('Настройки', {
            'fields': (
                'is_active', 
                'order'
            )
        }),
    )