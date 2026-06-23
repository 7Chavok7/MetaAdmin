from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from meta_app.employees.models import Employee, Skill, EmployeeSkill
from meta_app.employees.forms import EmployeeForm, EmployeeCreateForm
from meta_app.workstations.models import Workstation, EmployeeWorkstation
from .forms import LoginForm


def is_manager(user):
    """Проверка, является ли пользователь менеджером"""
    return user.is_authenticated and (user.is_superuser or user.is_manager)


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

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
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Неверный логин или пароль.')
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
    """Список всех сотрудников (исключая суперпользователей)"""
    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).order_by('last_name', 'first_name')
    return render(request, 'dashboard/employee_list.html', {
        'employees': employees,
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
def employee_detail(request, employee_id):
    """Карточка сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)

    # Обычный сотрудник видит только себя
    if not (request.user.is_superuser or request.user.is_manager):
        if request.user.id != employee.id:
            messages.error(request, 'У вас нет доступа к этой карточке')
            return redirect('dashboard:home')

    # Администратор скрыт от обычных пользователей
    if employee.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Доступ к карточке администратора ограничен')
        return redirect('dashboard:home')

    # Получаем навыки сотрудника
    skills = employee.employee_skills.select_related('skill').all()

    # Получаем участки сотрудника
    workstation_assignments = employee.workstation_assignments.select_related(
        'workstation').all()

    # Получаем записи о работе за последние 30 дней
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendances = employee.attendances.filter(
        record_date__gte=thirty_days_ago
    ).order_by('-record_date')

    # Считаем статистику за месяц
    total_hours = sum(
        [att.actual_hours for att in attendances if att.is_present])
    total_overtime = sum([att.overtime_hours for att in attendances])
    work_days = attendances.filter(is_present=True).count()
    avg_hours = total_hours / work_days if work_days > 0 else 0

    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee,
        'skills': skills,
        'workstation_assignments': workstation_assignments,
        'attendances': attendances[:10],
        'stats': {
            'total_hours': total_hours,
            'total_overtime': total_overtime,
            'work_days': work_days,
            'avg_hours': avg_hours,
        },
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
@user_passes_test(is_manager)
def employee_create(request):
    """Создание нового сотрудника"""
    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на создание сотрудников!')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
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

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на редактирование!')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee_obj = form.save(commit=False)
            employee_obj._updated_by_user = request.user
            employee_obj.save()

            messages.success(
                request, f'Данные сотрудника {employee.full_name} успешно обновлены!')
            return redirect('dashboard:home')
    else:
        form = EmployeeForm(instance=employee)
        if employee.birth_date:
            form.initial['birth_date'] = employee.birth_date.strftime(
                '%Y-%m-%d')
        if employee.hire_date:
            form.initial['hire_date'] = employee.hire_date.strftime('%Y-%m-%d')
        if employee.dismissal_date:
            form.initial['dismissal_date'] = employee.dismissal_date.strftime(
                '%Y-%m-%d')

    return render(request, 'dashboard/employee_edit.html', {
        'form': form,
        'employee': employee,
    })


@login_required
@user_passes_test(is_manager)
def employee_skills(request, employee_id):
    """Управление квалификациями сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на управление квалификациями!')
        return redirect('dashboard:home')

    employee_skills = employee.employee_skills.select_related('skill').all()
    existing_skill_ids = employee_skills.values_list('skill_id', flat=True)
    available_skills = Skill.objects.exclude(id__in=existing_skill_ids)

    return render(request, 'dashboard/employee_skills.html', {
        'employee': employee,
        'employee_skills': employee_skills,
        'available_skills': available_skills,
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
@user_passes_test(is_manager)
def employee_skill_add(request, employee_id):
    """Добавление квалификации сотруднику"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на добавление квалификаций!')
        return redirect('dashboard:home')

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        level = request.POST.get('level')

        if not skill_id:
            messages.error(request, 'Выберите навык')
            return redirect('dashboard:employee_skills', employee_id=employee.id)

        skill = get_object_or_404(Skill, id=skill_id)

        try:
            employee_skill = EmployeeSkill(
                employee=employee,
                skill=skill,
                level=level or 'middle'
            )
            employee_skill.save()
            messages.success(
                request, f'Квалификация "{skill.name}" успешно добавлена!')
        except IntegrityError:
            messages.error(request, 'Эта квалификация уже есть у сотрудника')

        return redirect('dashboard:employee_skills', employee_id=employee.id)

    return redirect('dashboard:employee_skills', employee_id=employee.id)


@login_required
@user_passes_test(is_manager)
def employee_skill_delete(request, employee_id, skill_id):
    """Удаление квалификации у сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на удаление квалификаций!')
        return redirect('dashboard:home')

    employee_skill = get_object_or_404(
        EmployeeSkill, employee=employee, skill_id=skill_id)
    skill_name = employee_skill.skill.name
    employee_skill.delete()

    messages.success(request, f'Квалификация "{skill_name}" успешно удалена!')
    return redirect('dashboard:employee_skills', employee_id=employee.id)


@login_required
@user_passes_test(is_manager)
def employee_workstations(request, employee_id):
    """Управление участками сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на управление участками!')
        return redirect('dashboard:home')

    assignments = employee.workstation_assignments.select_related(
        'workstation').all()
    existing_workstation_ids = assignments.values_list(
        'workstation_id', flat=True)
    available_workstations = Workstation.objects.filter(
        is_active=True).exclude(id__in=existing_workstation_ids)

    return render(request, 'dashboard/employee_workstations.html', {
        'employee': employee,
        'assignments': assignments,
        'available_workstations': available_workstations,
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
@user_passes_test(is_manager)
def employee_workstation_add(request, employee_id):
    """Добавление назначения на участок"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на добавление участков!')
        return redirect('dashboard:home')

    if request.method == 'POST':
        workstation_id = request.POST.get('workstation_id')
        is_primary = request.POST.get('is_primary') == 'on'

        if not workstation_id:
            messages.error(request, 'Выберите участок')
            return redirect('dashboard:employee_workstations', employee_id=employee.id)

        workstation = get_object_or_404(Workstation, id=workstation_id)

        if is_primary:
            EmployeeWorkstation.objects.filter(
                employee=employee, is_primary=True).update(is_primary=False)

        try:
            assignment = EmployeeWorkstation(
                employee=employee,
                workstation=workstation,
                is_primary=is_primary,
                created_by=request.user,
                updated_by=request.user,
            )
            assignment.save()
            messages.success(
                request, f'Назначение на "{workstation.name}" успешно добавлено!')
        except IntegrityError:
            messages.error(request, 'Этот участок уже назначен сотруднику')

        return redirect('dashboard:employee_workstations', employee_id=employee.id)

    return redirect('dashboard:employee_workstations', employee_id=employee.id)


@login_required
@user_passes_test(is_manager)
def employee_workstation_delete(request, employee_id, workstation_id):
    """Удаление назначения на участок"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на удаление участков!')
        return redirect('dashboard:home')

    assignment = get_object_or_404(
        EmployeeWorkstation, employee=employee, workstation_id=workstation_id)
    workstation_name = assignment.workstation.name
    assignment.delete()

    messages.success(
        request, f'Назначение на "{workstation_name}" успешно удалено!')
    return redirect('dashboard:employee_workstations', employee_id=employee.id)


@login_required
@user_passes_test(is_manager)
def employee_workstation_set_primary(request, employee_id, workstation_id):
    """Установка основного участка"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(
            request, 'У вас нет прав на изменение основного участка!')
        return redirect('dashboard:home')

    EmployeeWorkstation.objects.filter(
        employee=employee, is_primary=True).update(is_primary=False)
    assignment = get_object_or_404(
        EmployeeWorkstation, employee=employee, workstation_id=workstation_id)
    assignment.is_primary = True
    assignment.updated_by = request.user
    assignment.save()

    messages.success(
        request, f'Участок "{assignment.workstation.name}" установлен как основной!')
    return redirect('dashboard:employee_workstations', employee_id=employee.id)
