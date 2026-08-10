# meta_app/attendance/admin.py | A.Grachev
from django.contrib import admin
from .models import DailyAttendance, MonthlyWorkNorm, VacationRequest, KPI


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'record_date', 'workstation', 'status', 'is_present', 'actual_hours']
    list_filter = ['record_date', 'workstation', 'status', 'is_present']
    search_fields = ['employee__full_name']
    date_hierarchy = 'record_date'
    fieldsets = (
        ('Основное', {
            'fields': ('employee', 'record_date', 'workstation', 'status')
        }),
        ('Присутствие', {
            'fields': ('is_present', 'is_weekend_shift', 'start_time', 'end_time')
        }),
        ('Время', {
            'fields': ('hours_norm', 'overtime_hours', 'actual_hours', 'base_hours')
        }),
        ('Дополнительно', {
            'fields': ('note', 'created_by', 'updated_by')
        }),
    )


@admin.register(MonthlyWorkNorm)
class MonthlyWorkNormAdmin(admin.ModelAdmin):
    list_display = ['year', 'month', 'hours_norm']
    list_filter = ['year']
    fieldsets = (
        (None, {
            'fields': ('year', 'month', 'hours_norm')
        }),
    )


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['employee__last_name', 'employee__first_name', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('employee', 'start_date', 'end_date', 'status', 'comment')
        }),
        ('Обработка', {
            'fields': ('processed_by', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'bonus_amount', 'bonus_percent', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name']
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'type', 'is_active')
        }),
        ('Настройка бонуса', {
            'fields': ('bonus_amount', 'bonus_percent', 'skill_price'),
            'description': 'Можно заполнить несколько полей — бонусы суммируются'
        }),
    )