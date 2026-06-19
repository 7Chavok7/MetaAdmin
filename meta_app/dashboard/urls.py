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
    path('employees/create/', views.employee_create,
         name='employee_create'),  # ← добавить
    path('employees/<int:employee_id>/',
         views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/',
         views.employee_edit, name='employee_edit'),
]
