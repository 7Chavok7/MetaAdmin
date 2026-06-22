from django.urls import path
from . import views
from meta_app.attendance import views as attendance_views

app_name = 'dashboard'

urlpatterns = [
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Главная страница - теперь календарь!
    path('', attendance_views.attendance_calendar, name='home'),
    path('calendar/', attendance_views.attendance_calendar,
         name='attendance_calendar'),
    path('calendar/<int:year>/<int:month>/',
         attendance_views.attendance_calendar, name='attendance_calendar'),

    # Сотрудники
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:employee_id>/',
         views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/',
         views.employee_edit, name='employee_edit'),

    # Квалификации
    path('employees/<int:employee_id>/skills/',
         views.employee_skills, name='employee_skills'),
    path('employees/<int:employee_id>/skills/add/',
         views.employee_skill_add, name='employee_skill_add'),
    path('employees/<int:employee_id>/skills/<int:skill_id>/delete/',
         views.employee_skill_delete, name='employee_skill_delete'),

    # Участки
    path('employees/<int:employee_id>/workstations/',
         views.employee_workstations, name='employee_workstations'),
    path('employees/<int:employee_id>/workstations/add/',
         views.employee_workstation_add, name='employee_workstation_add'),
    path('employees/<int:employee_id>/workstations/<int:workstation_id>/delete/',
         views.employee_workstation_delete, name='employee_workstation_delete'),
    path('employees/<int:employee_id>/workstations/<int:workstation_id>/set-primary/',
         views.employee_workstation_set_primary, name='employee_workstation_set_primary'),

    # Учет времени
    path('attendance/', attendance_views.attendance_today, name='attendance_today'),
    path('attendance/all/', attendance_views.attendance_all, name='attendance_all'),
    path('attendance/create/<int:employee_id>/',
         attendance_views.attendance_create, name='attendance_create'),
    path('attendance/edit/<int:attendance_id>/',
         attendance_views.attendance_edit, name='attendance_edit'),
    path('attendance/delete/<int:attendance_id>/',
         attendance_views.attendance_delete, name='attendance_delete'),
]
