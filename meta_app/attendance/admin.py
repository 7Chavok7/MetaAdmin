# /meta_app/
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import VacationRequest


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
        'staus',
        'processed_at',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Основные данные', {
            'fields': ('employee', 'start_date', 'end_date', 'status')
        }),
    )