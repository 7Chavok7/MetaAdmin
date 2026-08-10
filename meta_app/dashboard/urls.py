# meta_app/dashboard/urls.py
from django.urls import path, include
from . import views
from meta_app.attendance import views as attendance_views

app_name = 'dashboard'

urlpatterns = [
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Главная страница
    path('', views.home_redirect, name='home'),
    path('calendar/', attendance_views.attendance_calendar, name='attendance_calendar'),
    path('calendar/<int:year>/<int:month>/', attendance_views.attendance_calendar, name='attendance_calendar'),

    # Дашборд директора
    path('director/', views.director_dashboard, name='director_dashboard'),

    # Сотрудники
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),

    # Квалификации
    path('employees/<int:employee_id>/skills/', views.employee_skills, name='employee_skills'),
    path('employees/<int:employee_id>/skills/add/', views.employee_skill_add, name='employee_skill_add'),
    path('employees/<int:employee_id>/skills/<int:skill_id>/delete/', views.employee_skill_delete, name='employee_skill_delete'),

    # Участки сотрудника
    path('employees/<int:employee_id>/workstations/', views.employee_workstations, name='employee_workstations'),
    path('employees/<int:employee_id>/workstations/add/', views.employee_workstation_add, name='employee_workstation_add'),
    path('employees/<int:employee_id>/workstations/<int:workstation_id>/delete/', views.employee_workstation_delete, name='employee_workstation_delete'),
    path('employees/<int:employee_id>/workstations/<int:workstation_id>/set-primary/', views.employee_workstation_set_primary, name='employee_workstation_set_primary'),

    # Учет времени (через attendance)
    path('attendance/', attendance_views.attendance_today, name='attendance_today'),
    path('attendance/all/', attendance_views.attendance_all, name='attendance_all'),
    path('attendance/create/<int:employee_id>/', attendance_views.attendance_create, name='attendance_create'),
    path('attendance/edit/<int:attendance_id>/', attendance_views.attendance_edit, name='attendance_edit'),
    path('attendance/delete/<int:attendance_id>/', attendance_views.attendance_delete, name='attendance_delete'),

    # Отчеты
    path('reports/hours/', attendance_views.report_employee_hours, name='report_hours'),
    path('norms/', attendance_views.norm_list, name='norm_list'),
    path('norms/edit/', attendance_views.norm_edit, name='norm_edit'),
    path('norms/edit/<int:norm_id>/', attendance_views.norm_edit, name='norm_edit'),
    path('norms/delete/<int:norm_id>/', attendance_views.norm_delete, name='norm_delete'),
    path('norms/fill/', attendance_views.norm_fill, name='norm_fill'),
    path('norms/bulk-edit/', attendance_views.norm_bulk_edit, name='norm_bulk_edit'),

    # Отпуска
    path('vacations/', attendance_views.vacation_list, name='vacation_list'),
    path('vacations/create/', attendance_views.vacation_create, name='vacation_create'),
    path('vacations/process/<int:vacation_id>/', attendance_views.vacation_process, name='vacation_process'),
    path('vacations/cancel/<int:vacation_id>/', attendance_views.vacation_cancel, name='vacation_cancel'),

    # Подразделения
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:department_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:department_id>/delete/', views.department_delete, name='department_delete'),

    # Участки (список)
    path('workstations/', views.workstation_list, name='workstation_list'),

    # KPI
    path('kpi/', views.kpi_list, name='kpi_list'),
    path('kpi/create/', views.kpi_create, name='kpi_create'),
    path('kpi/<int:kpi_id>/edit/', views.kpi_edit, name='kpi_edit'),
    path('kpi/<int:kpi_id>/delete/', views.kpi_delete, name='kpi_delete'),

    # Расчёт зарплаты
    # path('api/calculate-salary/', views.calculate_salary, name='calculate_salary'),
    # Зарплаты
    path('salary/', views.salary_table, name='salary_table'),
    path('api/calculate-month/', views.calculate_salary_month, name='calculate_salary_month'),
    path('salary/<int:employee_id>/<int:year>/<int:month>/', views.salary_detail, name='salary_detail'),

    # Мессенджер
    path('messenger/', include('meta_app.messenger.urls')),
]