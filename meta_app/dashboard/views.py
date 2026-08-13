# meta_app/dashboard/views.py | A.Grachev
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

from meta_app.attendance.services.kpi_service import KPIService
from meta_app.attendance.models import DailyAttendance, MonthlyWorkNorm, KPI, SalaryRecord
from meta_app.employees.models import Employee, Skill, EmployeeSkill
from meta_app.employees.forms import EmployeeForm, EmployeeCreateForm, EmployeeSelfEditForm
from meta_app.employees.decorators import (
    manager_or_director_required,
    director_required,
    is_manager,
    is_director
)
from meta_app.workstations.models import Workstation, EmployeeWorkstation, Department
from .forms import LoginForm


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_user_role(user):
    """Получить роль пользователя"""
    if not user.is_authenticated:
        return 'anonymous'
    if hasattr(user, 'role'):
        return user.role
    if user.is_superuser:
        return 'director'
    if user.is_manager:
        return 'manager'
    return 'employee'


def get_employees_for_user(user):
    if user.is_superuser or is_director(user):
        return Employee.objects.filter(is_superuser=False)
    elif is_manager(user):
        if user.department:
            return Employee.objects.filter(
                department=user.department,
                is_superuser=False
            )
        return Employee.objects.filter(is_superuser=False)
    else:
        return Employee.objects.filter(id=user.id)


# ============================================
# АУТЕНТИФИКАЦИЯ
# ============================================

def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        if is_manager(request.user):
            return redirect('dashboard:home')
        else:
            return redirect('messenger:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.full_name}!')

                if is_manager(user):
                    return redirect('dashboard:home')
                else:
                    return redirect('messenger:index')
            else:
                messages.error(request, 'Неверный логин или пароль.')
        else:
            messages.error(request, 'Ошибка входа. Проверьте введенные данные.')
    else:
        form = LoginForm()

    return render(request, 'dashboard/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('dashboard:login')


# ============================================
# ГЛАВНАЯ СТРАНИЦА / РЕДИРЕКТ
# ============================================

@login_required
def home_redirect(request):
    """Главная страница с редиректом в зависимости от роли"""
    if is_director(request.user):
        return redirect('dashboard:director_dashboard')
    elif is_manager(request.user):
        return redirect('dashboard:attendance_calendar')
    else:
        return redirect('messenger:index')


# ============================================
# ДИРЕКТОРСКИЙ ДАШБОРД
# ============================================

@login_required
@director_required
def director_dashboard(request):
    """Дашборд для директора"""
    
    today = timezone.now().date()
    
    # Статистика
    total_employees = Employee.objects.filter(is_active=True, is_superuser=False).count()
    total_departments = Department.objects.filter(is_active=True).count()
    total_workstations = Workstation.objects.filter(is_active=True).count()
    
    # Присутствие сегодня
    active_employees = Employee.objects.filter(is_active=True, is_superuser=False)
    total_today = active_employees.count()  # ← теперь это ВСЕ активные сотрудники
    
    # Получаем тех, кто отмечен присутствующим сегодня
    present_count = DailyAttendance.objects.filter(
        record_date=today,
        is_present=True
    ).values('employee').distinct().count()
    
    # Сотрудники без подразделения
    employees_without_dept = Employee.objects.filter(
        department__isnull=True,
        is_active=True,
        is_superuser=False
    ).count()
    
    # ✅ Дополнительно: кто в отпуске сегодня
    vacation_today = DailyAttendance.objects.filter(
        record_date=today,
        status='vacation'
    ).values('employee').distinct().count()
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_workstations': total_workstations,
        'employees_without_dept': employees_without_dept,
        'today_attendance': {
            'present': present_count,
            'total': total_today,
            'percent': round(present_count / total_today * 100, 1) if total_today > 0 else 0,
            'vacation': vacation_today,  # ← добавили
        },
        'recent_employees': Employee.objects.filter(
            is_active=True, is_superuser=False
        ).order_by('-created_at')[:5],
        'departments': Department.objects.filter(parent__isnull=True, is_active=True),
        'today': today,
        'current_time': timezone.now(),
    }
    
    return render(request, 'dashboard/director_dashboard.html', context)


# ============================================
# УПРАВЛЕНИЕ ПОДРАЗДЕЛЕНИЯМИ (CRUD)
# ============================================

@login_required
@director_required
def department_list(request):
    """Список всех подразделений"""
    departments = Department.objects.filter(is_active=True)
    return render(request, 'dashboard/department_list.html', {
        'departments': departments,
    })


@login_required
@director_required
def department_create(request):
    """Создание подразделения"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        parent_id = request.POST.get('parent')
        description = request.POST.get('description', '')
        
        if not name or not code:
            messages.error(request, 'Название и код обязательны')
            return redirect('dashboard:department_create')
        
        parent = None
        if parent_id:
            parent = get_object_or_404(Department, id=parent_id)
        
        try:
            department = Department.objects.create(
                name=name,
                code=code.upper(),
                parent=parent,
                description=description,
                is_active=True
            )
            messages.success(request, f'Подразделение "{name}" создано!')
            return redirect('dashboard:department_list')
        except IntegrityError:
            messages.error(request, 'Подразделение с таким кодом уже существует')
    
    parents = Department.objects.filter(parent__isnull=True, is_active=True)
    return render(request, 'dashboard/department_form.html', {
        'parents': parents,
        'title': 'Создать подразделение',
    })


@login_required
@director_required
def department_edit(request, department_id):
    """Редактирование подразделения"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        parent_id = request.POST.get('parent')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not code:
            messages.error(request, 'Название и код обязательны')
            return redirect('dashboard:department_edit', department_id=department.id)
        
        parent = None
        if parent_id:
            parent = get_object_or_404(Department, id=parent_id)
            # Нельзя назначить себя или потомка как родителя
            if parent.id == department.id:
                messages.error(request, 'Нельзя назначить подразделение родителем самого себя')
                return redirect('dashboard:department_edit', department_id=department.id)
        
        department.name = name
        department.code = code.upper()
        department.parent = parent
        department.description = description
        department.is_active = is_active
        department.save()
        
        messages.success(request, f'Подразделение "{name}" обновлено!')
        return redirect('dashboard:department_list')
    
    parents = Department.objects.filter(parent__isnull=True, is_active=True).exclude(id=department.id)
    return render(request, 'dashboard/department_form.html', {
        'department': department,
        'parents': parents,
        'title': 'Редактировать подразделение',
    })


@login_required
@director_required
def department_delete(request, department_id):
    """Удаление подразделения (мягкое)"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        # Проверяем, есть ли сотрудники в этом подразделении
        if department.employees.filter(is_active=True).exists():
            messages.error(
                request, 
                f'Нельзя удалить подразделение "{department.name}", '
                'так как в нём есть сотрудники. Сначала переместите их.'
            )
            return redirect('dashboard:department_list')
        
        department.is_active = False
        department.save()
        messages.success(request, f'Подразделение "{department.name}" помечено как неактивное')
        return redirect('dashboard:department_list')
    
    return render(request, 'dashboard/department_confirm_delete.html', {
        'department': department,
    })


# ============================================
# СОТРУДНИКИ (CRUD)
# ============================================

@login_required
@manager_or_director_required
def employee_list(request):
    """Список всех сотрудников (только для руководителей)"""
    employees = get_employees_for_user(request.user)
    
    # Поиск
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(patronymic__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Фильтр по статусу
    status = request.GET.get('status')
    if status == 'active':
        employees = employees.filter(is_active=True, dismissal_date__isnull=True)
    elif status == 'dismissed':
        employees = employees.filter(dismissal_date__isnull=False)
    elif status == 'no_department':
        employees = employees.filter(department__isnull=True, is_active=True)
    
    # Фильтр по подразделению
    department_id = request.GET.get('department')
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    # Сортировка
    sort = request.GET.get('sort', 'last_name')
    if sort == 'last_name':
        employees = employees.order_by('last_name', 'first_name')
    elif sort == 'hire_date':
        employees = employees.order_by('-hire_date')
    elif sort == 'department':
        employees = employees.order_by('department__name', 'last_name')
    
    return render(request, 'dashboard/employee_list.html', {
        'employees': employees,
        'can_edit': is_manager(request.user),
        'is_director': is_director(request.user),
        'departments': Department.objects.filter(is_active=True),
    })


@login_required
def employee_detail(request, employee_id):
    """Карточка сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Проверяем доступ
    is_self = request.user.id == employee.id
    is_admin_or_manager = is_manager(request.user)
    
    if not is_admin_or_manager and not is_self:
        messages.error(request, 'У вас нет доступа к этой карточке')
        return redirect('dashboard:employee_detail', employee_id=request.user.id)
    
    # Если сотрудник уволен и это не руководитель — запрещаем
    if employee.dismissal_date and employee.dismissal_date < timezone.now().date():
        if not is_admin_or_manager and not request.user.is_superuser:
            messages.error(request, 'Карточка уволенного сотрудника недоступна')
            return redirect('dashboard:home')
    
    # Получаем навыки и участки
    skills = employee.employee_skills.select_related('skill').all()
    workstation_assignments = employee.workstation_assignments.select_related('workstation').all()
    
    # Месяц и год
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Записи о работе
    attendances = employee.attendances.filter(
        record_date__year=year,
        record_date__month=month
    ).order_by('-record_date')
    
    # Статистика
    total_hours = sum([att.actual_hours for att in attendances if att.is_present])
    total_overtime = sum([att.overtime_hours for att in attendances])
    work_days = attendances.filter(is_present=True).count()
    avg_hours = total_hours / work_days if work_days > 0 else 0
    weekend_days = attendances.filter(is_weekend_shift=True).count()
    
    # Норма часов
    try:
        norm = MonthlyWorkNorm.objects.get(year=year, month=month)
        hours_norm = norm.hours_norm
    except MonthlyWorkNorm.DoesNotExist:
        hours_norm = 0
    
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    
    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee,
        'skills': skills,
        'workstation_assignments': workstation_assignments,
        'attendances': attendances[:5],
        'stats': {
            'total_hours': total_hours,
            'total_overtime': total_overtime,
            'work_days': work_days,
            'avg_hours': avg_hours,
            'hours_norm': hours_norm,
            'weekend_days': weekend_days,
        },
        'can_edit': is_manager(request.user) or is_self,
        'is_self': is_self,
        'month_name': months[month - 1],
        'month': month,
        'year': year,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'current_month': today.month,
        'current_year': today.year,
    })


@login_required
@manager_or_director_required
def employee_create(request):
    """Создание нового сотрудника"""
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.updated_by = request.user
            employee.save()
            
            messages.success(request, f'Сотрудник {employee.full_name} успешно создан!')
            return redirect('dashboard:employee_detail', employee_id=employee.id)
    else:
        form = EmployeeCreateForm()
    
    return render(request, 'dashboard/employee_create.html', {
        'form': form,
    })


@login_required
def employee_edit(request, employee_id):
    """Редактирование сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    is_self = request.user.id == employee.id
    is_admin_or_manager = is_manager(request.user)
    
    if not is_admin_or_manager and not is_self:
        messages.error(request, 'У вас нет прав на редактирование!')
        return redirect('dashboard:home')
    
    # Выбор формы в зависимости от прав
    if is_self and not is_admin_or_manager:
        form_class = EmployeeSelfEditForm
    else:
        form_class = EmployeeForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee_obj = form.save(commit=False)
            employee_obj._updated_by_user = request.user
            employee_obj.save()
            messages.success(request, f'Данные сотрудника {employee.full_name} успешно обновлены!')
            return redirect('dashboard:employee_detail', employee_id=employee.id)
    else:
        form = form_class(instance=employee)
        # Подготовка дат для формы
        if employee.birth_date:
            form.initial['birth_date'] = employee.birth_date.strftime('%Y-%m-%d')
        if employee.hire_date:
            form.initial['hire_date'] = employee.hire_date.strftime('%Y-%m-%d')
        if employee.dismissal_date:
            form.initial['dismissal_date'] = employee.dismissal_date.strftime('%Y-%m-%d')
    
    return render(request, 'dashboard/employee_edit.html', {
        'form': form,
        'employee': employee,
        'is_self': is_self,
        'can_edit': is_admin_or_manager or is_self,
    })


# ============================================
# КВАЛИФИКАЦИИ СОТРУДНИКА
# ============================================

@login_required
@manager_or_director_required
def employee_skills(request, employee_id):
    """Управление квалификациями сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    employee_skills = employee.employee_skills.select_related('skill').all()
    existing_skill_ids = employee_skills.values_list('skill_id', flat=True)
    available_skills = Skill.objects.exclude(id__in=existing_skill_ids)
    
    return render(request, 'dashboard/employee_skills.html', {
        'employee': employee,
        'employee_skills': employee_skills,
        'available_skills': available_skills,
        'can_edit': is_manager(request.user),
    })


@login_required
@manager_or_director_required
def employee_skill_add(request, employee_id):
    """Добавление квалификации сотруднику"""
    employee = get_object_or_404(Employee, id=employee_id)
    
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
            messages.success(request, f'Квалификация "{skill.name}" успешно добавлена!')
        except IntegrityError:
            messages.error(request, 'Эта квалификация уже есть у сотрудника')
        
        return redirect('dashboard:employee_skills', employee_id=employee.id)
    
    return redirect('dashboard:employee_skills', employee_id=employee.id)


@login_required
@manager_or_director_required
def employee_skill_delete(request, employee_id, skill_id):
    """Удаление квалификации у сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    employee_skill = get_object_or_404(EmployeeSkill, employee=employee, skill_id=skill_id)
    skill_name = employee_skill.skill.name
    employee_skill.delete()
    messages.success(request, f'Квалификация "{skill_name}" успешно удалена!')
    return redirect('dashboard:employee_skills', employee_id=employee.id)


# ============================================
# УЧАСТКИ СОТРУДНИКА
# ============================================

@login_required
@manager_or_director_required
def employee_workstations(request, employee_id):
    """Управление участками сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    assignments = employee.workstation_assignments.select_related('workstation').all()
    existing_workstation_ids = assignments.values_list('workstation_id', flat=True)
    available_workstations = Workstation.objects.filter(
        is_active=True
    ).exclude(id__in=existing_workstation_ids)
    
    return render(request, 'dashboard/employee_workstations.html', {
        'employee': employee,
        'assignments': assignments,
        'available_workstations': available_workstations,
        'can_edit': is_manager(request.user),
    })


@login_required
@manager_or_director_required
def employee_workstation_add(request, employee_id):
    """Добавление назначения на участок"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        workstation_id = request.POST.get('workstation_id')
        is_primary = request.POST.get('is_primary') == 'on'
        
        if not workstation_id:
            messages.error(request, 'Выберите участок')
            return redirect('dashboard:employee_workstations', employee_id=employee.id)
        
        workstation = get_object_or_404(Workstation, id=workstation_id)
        
        if is_primary:
            EmployeeWorkstation.objects.filter(
                employee=employee, is_primary=True
            ).update(is_primary=False)
        
        try:
            assignment = EmployeeWorkstation(
                employee=employee,
                workstation=workstation,
                is_primary=is_primary,
                created_by=request.user,
                updated_by=request.user,
            )
            assignment.save()
            messages.success(request, f'Назначение на "{workstation.name}" успешно добавлено!')
        except IntegrityError:
            messages.error(request, 'Этот участок уже назначен сотруднику')
        
        return redirect('dashboard:employee_workstations', employee_id=employee.id)
    
    return redirect('dashboard:employee_workstations', employee_id=employee.id)


@login_required
@manager_or_director_required
def employee_workstation_delete(request, employee_id, workstation_id):
    """Удаление назначения на участок"""
    employee = get_object_or_404(Employee, id=employee_id)
    assignment = get_object_or_404(EmployeeWorkstation, employee=employee, workstation_id=workstation_id)
    workstation_name = assignment.workstation.name
    assignment.delete()
    messages.success(request, f'Назначение на "{workstation_name}" успешно удалено!')
    return redirect('dashboard:employee_workstations', employee_id=employee.id)


@login_required
@manager_or_director_required
def employee_workstation_set_primary(request, employee_id, workstation_id):
    """Установка основного участка"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    EmployeeWorkstation.objects.filter(
        employee=employee, is_primary=True
    ).update(is_primary=False)
    
    assignment = get_object_or_404(EmployeeWorkstation, employee=employee, workstation_id=workstation_id)
    assignment.is_primary = True
    assignment.updated_by = request.user
    assignment.save()
    
    messages.success(request, f'Участок "{assignment.workstation.name}" установлен как основной!')
    return redirect('dashboard:employee_workstations', employee_id=employee.id)


# ============================================
# УПРАВЛЕНИЕ УЧАСТКАМИ (CRUD)
# ============================================

@login_required
@manager_or_director_required
def workstation_list(request):
    """Список всех участков"""
    workstations = Workstation.objects.filter(is_active=True).select_related('department').order_by('department__name', 'name')
    
    department_id = request.GET.get('department')
    if department_id:
        workstations = workstations.filter(department_id=department_id)
    
    search = request.GET.get('search')
    if search:
        workstations = workstations.filter(
            Q(name__icontains=search) |
            Q(short_name__icontains=search) |
            Q(department__name__icontains=search)
        )
    
    departments = Department.objects.filter(is_active=True)
    
    return render(request, 'dashboard/workstation_list.html', {
        'workstations': workstations,
        'departments': departments,
        'selected_department': department_id,
        'search': search,
        'is_director': is_director(request.user),
        'is_deputy': request.user.role == 'deputy' if hasattr(request.user, 'role') else False,
    })


@login_required
@director_required
def workstation_create(request):
    """Создание участка"""
    if request.method == 'POST':
        name = request.POST.get('name')
        short_name = request.POST.get('short_name')
        department_id = request.POST.get('department')
        schedule_type = request.POST.get('schedule_type', '5_2')
        work_start = request.POST.get('work_start', '08:00')
        work_end = request.POST.get('work_end', '17:00')
        hours_per_day = request.POST.get('hours_per_day', 8)
        color = request.POST.get('color', '#007bff')
        is_active = request.POST.get('is_active') == 'on'
        
        if not name or not short_name:
            messages.error(request, 'Название и сокращение обязательны')
            return redirect('dashboard:workstation_create')
        
        department = None
        if department_id:
            department = get_object_or_404(Department, id=department_id)
        
        Workstation.objects.create(
            name=name,
            short_name=short_name,
            department=department,
            schedule_type=schedule_type,
            work_start=work_start,
            work_end=work_end,
            hours_per_day=hours_per_day,
            color=color,
            is_active=is_active,
            created_by=request.user,
            updated_by=request.user,
        )
        
        messages.success(request, f'Участок "{name}" создан!')
        return redirect('dashboard:workstation_list')
    
    departments = Department.objects.filter(is_active=True)
    return render(request, 'dashboard/workstation_form.html', {
        'departments': departments,
        'title': 'Создать участок',
        'workstation': None,
    })


@login_required
@director_required
def workstation_edit(request, workstation_id):
    """Редактирование участка"""
    workstation = get_object_or_404(Workstation, id=workstation_id)
    
    if request.method == 'POST':
        workstation.name = request.POST.get('name')
        workstation.short_name = request.POST.get('short_name')
        department_id = request.POST.get('department')
        workstation.schedule_type = request.POST.get('schedule_type', '5_2')
        workstation.work_start = request.POST.get('work_start', '08:00')
        workstation.work_end = request.POST.get('work_end', '17:00')
        workstation.hours_per_day = request.POST.get('hours_per_day', 8)
        workstation.color = request.POST.get('color', '#007bff')
        workstation.is_active = request.POST.get('is_active') == 'on'
        workstation.updated_by = request.user
        
        if not workstation.name or not workstation.short_name:
            messages.error(request, 'Название и сокращение обязательны')
            return redirect('dashboard:workstation_edit', workstation_id=workstation.id)
        
        workstation.department = None
        if department_id:
            workstation.department = get_object_or_404(Department, id=department_id)
        
        workstation.save()
        
        messages.success(request, f'Участок "{workstation.name}" обновлён!')
        return redirect('dashboard:workstation_list')
    
    departments = Department.objects.filter(is_active=True)
    return render(request, 'dashboard/workstation_form.html', {
        'departments': departments,
        'title': 'Редактировать участок',
        'workstation': workstation,
    })


@login_required
@director_required
def workstation_delete(request, workstation_id):
    """Удаление участка (мягкое)"""
    workstation = get_object_or_404(Workstation, id=workstation_id)
    
    if request.method == 'POST':
        # Проверяем, есть ли сотрудники, привязанные к этому участку
        if workstation.employee_assignments.exists():
            messages.error(
                request, 
                f'Нельзя удалить участок "{workstation.name}", '
                'так как на нём есть сотрудники. Сначала переместите их.'
            )
            return redirect('dashboard:workstation_list')
        
        workstation.is_active = False
        workstation.save()
        messages.success(request, f'Участок "{workstation.name}" помечен как неактивный')
        return redirect('dashboard:workstation_list')
    
    return render(request, 'dashboard/workstation_confirm_delete.html', {
        'workstation': workstation,
    })


# ============================================
# УПРАВЛЕНИЕ KPI (CRUD)
# ============================================

@login_required
@director_required
def kpi_list(request):
    """Список всех KPI"""
    kpis = KPI.objects.all().order_by('is_active', 'name')
    return render(request, 'dashboard/kpi_list.html', {
        'kpis': kpis,
    })


@login_required
@director_required
def kpi_create(request):
    """Создание KPI"""
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        bonus_amount = request.POST.get('bonus_amount', 0)
        bonus_percent = request.POST.get('bonus_percent', 0)
        skill_price = request.POST.get('skill_price', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            messages.error(request, 'Название KPI обязательно')
            return redirect('dashboard:kpi_create')
        
        KPI.objects.create(
            name=name,
            type=type,
            bonus_amount=bonus_amount,
            bonus_percent=bonus_percent,
            skill_price=skill_price,
            is_active=is_active,
        )
        messages.success(request, f'KPI "{name}" создан!')
        return redirect('dashboard:kpi_list')
    
    return render(request, 'dashboard/kpi_form.html', {
        'title': 'Создать KPI',
        'kpi': None,
        'type_choices': KPI.TYPE_CHOICES,
    })


@login_required
@director_required
def kpi_edit(request, kpi_id):
    """Редактирование KPI"""
    kpi = get_object_or_404(KPI, id=kpi_id)
    
    if request.method == 'POST':
        kpi.name = request.POST.get('name')
        kpi.type = request.POST.get('type')
        kpi.bonus_amount = request.POST.get('bonus_amount', 0)
        kpi.bonus_percent = request.POST.get('bonus_percent', 0)
        kpi.skill_price = request.POST.get('skill_price', 0)
        kpi.is_active = request.POST.get('is_active') == 'on'
        kpi.save()
        
        messages.success(request, f'KPI "{kpi.name}" обновлён!')
        return redirect('dashboard:kpi_list')
    
    return render(request, 'dashboard/kpi_form.html', {
        'title': 'Редактировать KPI',
        'kpi': kpi,
        'type_choices': KPI.TYPE_CHOICES,
    })


@login_required
@director_required
def kpi_delete(request, kpi_id):
    """Удаление KPI"""
    kpi = get_object_or_404(KPI, id=kpi_id)
    
    if request.method == 'POST':
        name = kpi.name
        kpi.delete()
        messages.success(request, f'KPI "{name}" удалён!')
        return redirect('dashboard:kpi_list')
    
    return render(request, 'dashboard/kpi_confirm_delete.html', {
        'kpi': kpi,
    })


# ============================================
# РАСЧЁТ ЗАРПЛАТЫ
# ============================================

@login_required
@director_required
@csrf_exempt
def calculate_salary(request):
    """API для расчёта зарплаты за текущий месяц"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    
    try:
        year = timezone.now().year
        month = timezone.now().month
        
        employees = Employee.objects.filter(is_active=True, is_superuser=False)
        
        total_salary = Decimal('0')
        results = []
        
        for employee in employees:
            kpi_results = KPIService.calculate_all_kpis_for_month(employee, year, month)
            
            base_salary = Decimal(str(employee.base_salary or 0))
            total_bonus = sum([Decimal(str(r['bonus'])) for r in kpi_results], Decimal('0'))
            total = base_salary + total_bonus
            
            total_salary += total
            results.append({
                'employee': employee.full_name,
                'base_salary': float(base_salary),
                'bonus': float(total_bonus),
                'total': float(total),
            })
        
        return JsonResponse({
            'success': True,
            'message': f'Зарплата рассчитана! Всего: {total_salary:.2f} руб.',
            'total_salary': float(total_salary),
            'employees': results,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)
        
        
@login_required
@director_required
def salary_table(request):
    """Страница таблицы зарплат"""
    
    current_year = timezone.now().year
    year = int(request.GET.get('year', current_year))
    months = range(1, 13)
    
    # Получаем всех сотрудников с подразделениями
    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).select_related('department').order_by('department__name', 'last_name')
    
    # ============================================
    # ГРУППИРУЕМ ПО РОДИТЕЛЬСКИМ ПОДРАЗДЕЛЕНИЯМ
    # ============================================
    # Сначала группируем по родительскому подразделению
    parent_groups = {}
    
    for emp in employees:
        if emp.department:
            # Получаем родительское подразделение (верхний уровень)
            parent = emp.department.parent or emp.department
            parent_name = parent.name
            
            if parent_name not in parent_groups:
                parent_groups[parent_name] = {
                    'parent': parent,
                    'children': {}
                }
            
            # Группируем по дочерним подразделениям внутри родителя
            child_name = emp.department.name
            if child_name not in parent_groups[parent_name]['children']:
                parent_groups[parent_name]['children'][child_name] = {
                    'department': emp.department,
                    'employees': []
                }
            
            parent_groups[parent_name]['children'][child_name]['employees'].append(emp)
        else:
            # Сотрудники без подразделения
            if 'Без подразделения' not in parent_groups:
                parent_groups['Без подразделения'] = {
                    'parent': None,
                    'children': {
                        'Без подразделения': {
                            'department': None,
                            'employees': []
                        }
                    }
                }
            parent_groups['Без подразделения']['children']['Без подразделения']['employees'].append(emp)
    
    # ============================================
    # СОБИРАЕМ ДАННЫЕ ДЛЯ ТАБЛИЦЫ
    # ============================================
    table_data = []
    
    # Сортируем родительские подразделения
    sorted_parents = sorted(parent_groups.keys())
    
    for parent_name in sorted_parents:
        parent_group = parent_groups[parent_name]
        
        # Для каждого родителя создаём блок
        parent_data = {
            'parent_name': parent_name,
            'parent': parent_group['parent'],
            'children': []
        }
        
        # Сортируем дочерние подразделения
        sorted_children = sorted(parent_group['children'].keys())
        
        for child_name in sorted_children:
            child_data = parent_group['children'][child_name]
            child_dept = child_data['department']
            child_employees = child_data['employees']
            
            # Собираем данные по каждому сотруднику
            employees_data = []
            for employee in child_employees:
                # Получаем зарплаты за каждый месяц
                salary_records = SalaryRecord.objects.filter(
                    employee=employee,
                    year=year
                ).order_by('month')
                
                month_salaries = [None] * 12
                for record in salary_records:
                    month_salaries[record.month - 1] = {
                        'total': float(record.total_salary),
                        'base': float(record.base_salary),
                        'bonus': float(record.kpi_bonus),
                        'is_calculated': record.is_calculated,
                    }
                
                employees_data.append({
                    'employee': employee,
                    'salaries': month_salaries,
                })
            
            parent_data['children'].append({
                'department_name': child_name,
                'department': child_dept,
                'employees': employees_data,
            })
        
        table_data.append(parent_data)
    
    # Проверяем, какие месяцы уже рассчитаны
    calculated_months = set()
    for record in SalaryRecord.objects.filter(year=year).values_list('month', flat=True).distinct():
        calculated_months.add(record)
    
    current_month = timezone.now().month
    
    context = {
        'table_data': table_data,
        'year': year,
        'current_year': current_year,
        'months': months,
        'calculated_months': calculated_months,
        'current_month': current_month,
        'month_names': ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                        'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
    }
    
    return render(request, 'dashboard/salary_table.html', context)


@login_required
@director_required
@csrf_exempt
def calculate_salary_month(request):
    """API для расчёта зарплаты за конкретный месяц"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    
    try:
        data = json.loads(request.body)
        year = data.get('year')
        month = data.get('month')
        
        if not year or not month:
            return JsonResponse({'error': 'Укажите год и месяц'}, status=400)
        
        # Рассчитываем зарплаты
        results = KPIService.calculate_all_salaries(
            year, month, calculated_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Зарплата за {month}.{year} рассчитана!',
            'count': len(results),
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # ← Добавить для отладки
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)
        
        
@login_required
@director_required
def salary_detail(request, employee_id, year, month):
    """Детальный расчёт зарплаты сотрудника за месяц"""
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Получаем запись о зарплате
    salary_record = SalaryRecord.objects.filter(
        employee=employee,
        year=year,
        month=month
    ).first()
    
    # Если записи нет — рассчитываем
    if not salary_record:
        salary_record = KPIService.calculate_and_save_salary(
            employee, year, month, calculated_by=request.user
        )
    
    # Получаем детали KPI
    kpi_details = salary_record.kpi_details if salary_record else {}
    
    # Получаем все KPI
    all_kpis = KPI.objects.filter(is_active=True)
    
    # Получаем количество навыков сотрудника
    skill_count = employee.employee_skills.count()
    
    # ============================================
    # Получаем данные о посещаемости для KPI "Нет пропусков"
    # ============================================
    from meta_app.attendance.services.kpi_service import KPIService
    total_workdays = KPIService.get_workdays_in_month(employee, year, month)
    
    attendances = DailyAttendance.objects.filter(
        employee=employee,
        record_date__year=year,
        record_date__month=month
    )
    
    present_days = attendances.filter(status='present').count()
    absence_days = attendances.filter(
        status__in=['absent', 'sick', 'vacation']
    ).count()
    has_any_record = attendances.exists()
    
    # Формируем список KPI с результатами
    kpi_results = []
    for kpi in all_kpis:
        detail = kpi_details.get(kpi.name, {})
        
        # Для KPI "Нет пропусков" добавляем данные о днях
        absence_data = None
        if kpi.type == 'no_absence':
            absence_data = {
                'total_workdays': total_workdays,
                'present_days': present_days,
                'absence_days': absence_days,
                'has_any_record': has_any_record,
            }
        
        # Для KPI "Есть навыки" добавляем количество навыков
        skill_count_data = None
        bonus_skills_count = 0
        if kpi.type == 'has_skills':
            skill_count_data = skill_count
            if skill_count >= 2:
                bonus_skills_count = skill_count - 1
            else:
                bonus_skills_count = 0
        
        kpi_results.append({
            'kpi': kpi,
            'completed': detail.get('completed', False),
            'bonus': detail.get('bonus', 0),
            'skill_count': skill_count_data,
            'bonus_skills_count': bonus_skills_count,
            'absence_data': absence_data,  # ← добавить
        })
    
    # ============================================
    # ФОРМИРУЕМ КАЛЕНДАРЬ НА МЕСЯЦ
    # ============================================
    import calendar
    from datetime import date
    
    # Получаем все записи за месяц
    attendances = DailyAttendance.objects.filter(
        employee=employee,
        record_date__year=year,
        record_date__month=month
    )
    
    # Создаём словарь для быстрого доступа по дню
    attendance_map = {}
    for att in attendances:
        attendance_map[att.record_date.day] = att
    
    # Формируем календарь
    today = timezone.now().date()
    _, days_in_month = calendar.monthrange(year, month)
    
    calendar_days = []
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        is_weekend = current_date.weekday() >= 5
        is_today = current_date == today
        
        att = attendance_map.get(day)
        
        if att:
            # Есть запись
            status = att.status
            hours = att.actual_hours
        elif is_weekend:
            # Выходной день без записи
            status = 'weekend'
            hours = 0
        else:
            # Нет записи в рабочий день
            status = 'no_record'
            hours = 0
        
        calendar_days.append({
            'day': day,
            'date': current_date,
            'is_weekend': is_weekend,
            'is_today': is_today,
            'status': status,
            'hours': float(hours) if hours else 0,
        })
    
    # Статистика
    work_days = attendances.filter(is_weekend_shift=False).count()
    weekend_works = attendances.filter(is_weekend_shift=True).count()
    total_days = attendances.count()
    total_hours = sum([att.actual_hours for att in attendances])
    
    context = {
        'employee': employee,
        'year': year,
        'month': month,
        'month_name': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
        'salary_record': salary_record,
        'kpi_results': kpi_results,
        'calendar_days': calendar_days,
        'work_days': work_days,
        'weekend_days': weekend_works,
        'total_days': total_days,
        'total_hours': float(total_hours),
        'today': today,
    }
    
    return render(request, 'dashboard/salary_detail.html', context)