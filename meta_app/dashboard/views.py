# meta_app/dashboard/views.py | A.Grachev
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from meta_app.attendance.models import DailyAttendance, MonthlyWorkNorm
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
    today_attendances = DailyAttendance.objects.filter(record_date=today)
    present_count = today_attendances.filter(is_present=True).count()
    total_today = today_attendances.count()
    
    # Сотрудники без подразделения
    employees_without_dept = Employee.objects.filter(
        department__isnull=True,
        is_active=True,
        is_superuser=False
    ).count()
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_workstations': total_workstations,
        'employees_without_dept': employees_without_dept,
        'today_attendance': {
            'present': present_count,
            'total': total_today,
            'percent': round(present_count / total_today * 100, 1) if total_today > 0 else 0,
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


@login_required
@manager_or_director_required
def workstation_list(request):
    """Список всех участков"""
    from meta_app.workstations.models import Workstation
    
    # Получаем все активные участки с подразделениями
    workstations = Workstation.objects.filter(is_active=True).select_related('department').order_by('department__name', 'name')
    
    # Фильтр по подразделению
    department_id = request.GET.get('department')
    if department_id:
        workstations = workstations.filter(department_id=department_id)
    
    # Поиск
    search = request.GET.get('search')
    if search:
        workstations = workstations.filter(
            Q(name__icontains=search) |
            Q(short_name__icontains=search) |
            Q(department__name__icontains=search)
        )
    
    # Список подразделений для фильтра
    departments = Department.objects.filter(is_active=True)
    
    return render(request, 'dashboard/workstation_list.html', {
        'workstations': workstations,
        'departments': departments,
        'selected_department': department_id,
        'search': search,
    })