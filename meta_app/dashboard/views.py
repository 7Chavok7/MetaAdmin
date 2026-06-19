from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from meta_app.employees.models import Employee
from meta_app.employees.forms import EmployeeForm, EmployeeCreateForm
from meta_app.workstations.models import EmployeeWorkstation
from .forms import LoginForm


def is_manager(user):
    """Проверка, является ли пользователь менеджером"""
    return user.is_authenticated and (user.is_superuser or user.is_manager)


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('dashboard:employee_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f'Добро пожаловать, {user.full_name}!')
                return redirect('dashboard:employee_list')
            else:
                messages.error(request, 'Неверный табельный номер или пароль.')
        else:
            messages.error(
                request, 'Ошибка входа. Проверьте введенные данные.')
    else:
        form = LoginForm()

    return render(request, 'dashboard/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('dashboard:login')


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

    # Получаем навыки сотрудника
    skills = employee.employee_skills.select_related('skill').all()

    # Получаем участки сотрудника
    workstation_assignments = employee.workstation_assignments.select_related(
        'workstation').all()

    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee,
        'skills': skills,
        'workstation_assignments': workstation_assignments,
        'can_edit': request.user.is_superuser,
    })


@login_required
@user_passes_test(is_manager)
def employee_create(request):
    """Создание нового сотрудника"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на создание сотрудников!')
        return redirect('dashboard:employee_list')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # Получаем текущего пользователя как Employee
            current_user = Employee.objects.get(id=request.user.id)

            employee = form.save(commit=False)
            employee.created_by = current_user
            employee.updated_by = current_user
            employee.save()

            messages.success(
                request, f'Сотрудник {employee.full_name} успешно создан!')
            return redirect('dashboard:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeCreateForm()

    return render(request, 'dashboard/employee_create.html', {
        'form': form,
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
            # Сохраняем сотрудника с указанием, кто редактирует
            employee_obj = form.save(commit=False)
            employee_obj._updated_by_user = request.user
            employee_obj.save()

            messages.success(
                request, f'Данные сотрудника {employee.full_name} успешно обновлены!')
            return redirect('dashboard:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'dashboard/employee_edit.html', {
        'form': form,
        'employee': employee,
    })
