from django.contrib import admin
from .models import Workstation, EmployeeWorkstation


class EmployeeWorkstationInline(admin.TabularInline):
    model = EmployeeWorkstation
    extra = 1
    fields = ['workstation', 'is_primary', 'assigned_date', 'note']
    autocomplete_fields = ['workstation']


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'schedule_type',
                    'work_start', 'work_end', 'hours_per_day', 'is_active']
    list_filter = ['schedule_type', 'is_active']
    search_fields = ['name', 'short_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'short_name', 'color', 'is_active')
        }),
        ('Режим работы', {
            'fields': ('schedule_type', 'work_start', 'work_end', 'hours_per_day')
        }),
        ('Аудит', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmployeeWorkstation)
class EmployeeWorkstationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'workstation', 'is_primary', 'assigned_date']
    list_filter = ['workstation', 'is_primary']
    search_fields = ['employee__full_name', 'workstation__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
