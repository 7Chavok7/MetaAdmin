from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Сотрудники
    path('', views.employee_list, name='employee_list'),
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
]
