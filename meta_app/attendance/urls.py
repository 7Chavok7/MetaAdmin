# meta_app/attendance/urls.py
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Учет времени
    path('today/', views.attendance_today, name='attendance_today'),
    path('all/', views.attendance_all, name='attendance_all'),
    path('create/<int:employee_id>/', views.attendance_create, name='attendance_create'),
    path('edit/<int:attendance_id>/', views.attendance_edit, name='attendance_edit'),
    path('delete/<int:attendance_id>/', views.attendance_delete, name='attendance_delete'),
    
    # Календарь
    path('calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('calendar/<int:year>/<int:month>/', views.attendance_calendar, name='attendance_calendar'),
    
    # Отчеты
    path('reports/hours/', views.report_employee_hours, name='report_hours'),
    path('norms/', views.norm_list, name='norm_list'),
    path('norms/edit/', views.norm_edit, name='norm_edit'),
    path('norms/edit/<int:norm_id>/', views.norm_edit, name='norm_edit'),
    path('norms/delete/<int:norm_id>/', views.norm_delete, name='norm_delete'),
    path('norms/fill/', views.norm_fill, name='norm_fill'),
    path('norms/bulk-edit/', views.norm_bulk_edit, name='norm_bulk_edit'),
    
    # Отпуска
    path('vacations/', views.vacation_list, name='vacation_list'),
    path('vacations/create/', views.vacation_create, name='vacation_create'),
    path('vacations/process/<int:vacation_id>/', views.vacation_process, name='vacation_process'),
    path('vacations/cancel/<int:vacation_id>/', views.vacation_cancel, name='vacation_cancel'),
]