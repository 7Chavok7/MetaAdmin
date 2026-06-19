from django.shortcuts import render, get_object_or_404
from meta_app.employees.models import Employee


def employee_list(request):
    """Список всех сотрудников"""
    employees = Employee.objects.filter(
        is_active=True).order_by('last_name', 'first_name')
    return render(request, 'dashboard/employee_list.html', {
        'employees': employees
    })


def employee_detail(request, employee_id):
    """Карточка сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee
    })
