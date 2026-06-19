from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/',
         views.employee_detail, name='employee_detail'),
]
