from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from meta_app.employees.models import Employee
from meta_app.employees.forms import EmployeeForm


def is_manager(user):
    """Проверка, является ли пользователь менеджером"""
    return user.is_authenticated and (user.is_superuser or user.is_manager)


@login_required
@user_passes_test(is_manager)
def employee_list(request):
    """Список всех сотрудников"""
    employees = Employee.objects.filter(
        is_active=True).order_by('last_name', 'first_name')
    return render(request, 'dashboard/employee_list.html', {
        'employees': employees
    })


@login_required
@user_passes_test(is_manager)
def employee_detail(request, employee_id):
    """Карточка сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    skills = employee.employee_skills.select_related('skill').all()

    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee,
        'skills': skills,
        'can_edit': request.user.is_superuser,
    })


@login_required
@user_passes_test(is_manager)
def employee_edit(request, employee_id):
    """Редактирование сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)

    # Только суперпользователь может редактировать
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на редактирование!')
        return redirect('dashboard:employee_detail', employee_id=employee.id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Данные сотрудника {employee.full_name} успешно обновлены!')
            return redirect('dashboard:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'dashboard/employee_edit.html', {
        'form': form,
        'employee': employee,
    })
