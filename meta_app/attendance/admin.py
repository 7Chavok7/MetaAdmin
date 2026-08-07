# /meta_app/
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import VacationRequest, KPI


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    """Админка запросов на отпуск"""

    list_display = [
        'employee',
        'start_date',
        'end_date',
        'status',
    ]
    list_filter = [
        'employee',
        'status',
    ]
    search_fields = [
        'employee',
        'status',
        'processed_by',   
    ]
    readonly_fields = [
        'status',
        'processed_at',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Основные данные', {
            'fields': ('employee', 'start_date', 'end_date', 'status')
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