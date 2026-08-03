from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from meta_app.employees.models import Employee
from meta_app.workstations.models import EmployeeWorkstation
from .models import DailyAttendance, MonthlyWorkNorm, VacationRequest
from .forms import (
    AttendanceForm, 
    MonthlyWorkNormForm, 
    VacationRequestForm, 
    VacationRequestProcessForm
)

def is_manager(user):
    return user.is_authenticated and (user.is_superuser or user.is_manager)


@login_required
@user_passes_test(is_manager)
def attendance_today(request):
    """Главная страница учета времени на сегодня"""
    today = timezone.now().date()

    today = timezone.now().date()

    if request.user.is_superuser or request.user.is_manager:
        employees = Employee.objects.filter(
            is_active=True,
            is_superuser=False
        ).order_by('last_name', 'first_name')
    else:
        employees = Employee.objects.filter(id=request.user.id)

    employee_data = []
    for employee in employees:
        try:
            attendance = DailyAttendance.objects.get(
                employee=employee, record_date=today)
            employee_data.append({
                'employee': employee,
                'attendance': attendance,
            })
        except DailyAttendance.DoesNotExist:
            employee_data.append({
                'employee': employee,
                'attendance': None,
            })

    return render(request, 'attendance/today.html', {
        'employee_data': employee_data,
        'today': today,
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
@user_passes_test(is_manager)
def attendance_create(request, employee_id):
    """Создание записи за любой день"""
    employee = get_object_or_404(Employee, id=employee_id)

    # Проверяем, не уволен ли сотрудник
    if employee.dismissal_date:
        date_param = request.GET.get('date')
        if date_param:
            try:
                selected_date = datetime.strptime(
                    date_param, '%Y-%m-%d').date()
                if selected_date > employee.dismissal_date:
                    messages.error(
                        request, 'Нельзя создавать записи после даты увольнения!')
                    return redirect('dashboard:home')
            except ValueError:
                pass
            
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        next_url = request.POST.get('next')

        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = employee
            attendance.created_by = request.user
            attendance.updated_by = request.user

            if not attendance.start_time and attendance.workstation:
                attendance.start_time = attendance.workstation.work_start
                attendance.end_time = attendance.workstation.work_end
                attendance.hours_norm = attendance.workstation.hours_per_day
            elif not attendance.start_time:
                attendance.start_time = '08:00'
                attendance.end_time = '17:00'
                attendance.hours_norm = 8.0

            existing = DailyAttendance.objects.filter(
                employee=employee,
                record_date=attendance.record_date
            ).first()

            if existing:
                messages.warning(
                    request,
                    f'У {employee.full_name} уже есть запись на {attendance.record_date}. Перейдите к редактированию.'
                )
                return redirect('dashboard:attendance_edit', attendance_id=existing.id)

            attendance.save()
            messages.success(
                request, f'Запись для {employee.full_name} на {attendance.record_date} создана!')

            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
    else:
        date_param = request.GET.get('date')

        if date_param:
            try:
                record_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                record_date = timezone.now().date()
        else:
            record_date = timezone.now().date()

        next_url = request.GET.get('next')

        default_workstation = None
        primary_assignment = employee.workstation_assignments.filter(
            is_primary=True).first()
        if primary_assignment:
            default_workstation = primary_assignment.workstation

        initial_data = {
            'record_date': record_date.strftime('%Y-%m-%d'),
        }

        if default_workstation:
            initial_data['workstation'] = default_workstation
            initial_data['start_time'] = default_workstation.work_start
            initial_data['end_time'] = default_workstation.work_end
        else:
            initial_data['start_time'] = '08:00'
            initial_data['end_time'] = '17:00'

        form = AttendanceForm(initial=initial_data)

    return render(request, 'attendance/create.html', {
        'form': form,
        'employee': employee,
        'next_url': next_url,
    })


@login_required
@user_passes_test(is_manager)
def attendance_edit(request, attendance_id):
    """Редактирование записи"""
    attendance = get_object_or_404(DailyAttendance, id=attendance_id)
    next_url = request.GET.get('next')

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на редактирование!')
        return redirect('dashboard:attendance_today')

    # Проверяем, не уволен ли сотрудник и не превышает ли дата записи дату увольнения
    if attendance.employee.dismissal_date:
        if attendance.record_date > attendance.employee.dismissal_date:
            messages.error(
                request, 'Нельзя редактировать записи после даты увольнения!')
            return redirect('dashboard:attendance_today')

    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        next_url = request.POST.get('next')
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.updated_by = request.user
            attendance.save()

            messages.success(request, 'Запись обновлена!')

            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
    else:
        form = AttendanceForm(instance=attendance)
        form.initial['record_date'] = attendance.record_date.strftime(
            '%Y-%m-%d')

    return render(request, 'attendance/edit.html', {
        'form': form,
        'attendance': attendance,
        'next_url': next_url,
    })


@login_required
@user_passes_test(is_manager)
def attendance_delete(request, attendance_id):
    """Удаление записи"""
    attendance = get_object_or_404(DailyAttendance, id=attendance_id)

    if not (request.user.is_superuser or request.user.is_manager):
        messages.error(request, 'У вас нет прав на удаление!')
        return redirect('dashboard:home')

    employee_name = attendance.employee.full_name
    attendance.delete()
    messages.warning(request, f'Запись для {employee_name} удалена!')
    return redirect('dashboard:home')


@login_required
@user_passes_test(is_manager)
def attendance_all(request):
    """Список всех записей с фильтром"""
    employee_id = request.GET.get('employee')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Базовый запрос
    if request.user.is_superuser or request.user.is_manager:
        attendances = DailyAttendance.objects.filter(
            employee__is_superuser=False)
    else:
        attendances = DailyAttendance.objects.filter(employee=request.user)

    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    if date_from:
        attendances = attendances.filter(record_date__gte=date_from)
    if date_to:
        attendances = attendances.filter(record_date__lte=date_to)

    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).order_by('last_name', 'first_name')

    return render(request, 'attendance/all.html', {
        'attendances': attendances,
        'employees': employees,
        'selected_employee': employee_id,
        'date_from': date_from,
        'date_to': date_to,
        'can_edit': request.user.is_superuser or request.user.is_manager,
    })


@login_required
@user_passes_test(is_manager)
def attendance_calendar(request, year=None, month=None):
    """Календарь посещаемости с группировкой по основным участкам"""
    from calendar import monthrange
    from datetime import date
    from collections import defaultdict
    from meta_app.workstations.models import Workstation

    today = timezone.now().date()
    if not year:
        year = today.year
    if not month:
        month = today.month

    _, days_in_month = monthrange(year, month)

    days_in_month_list = []
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        days_in_month_list.append({
            'day': day,
            'date': current_date,
            'weekday': current_date.weekday(),
            'weekday_short': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][current_date.weekday()],
            'is_weekend': current_date.weekday() >= 5,
        })

    # Получаем всех сотрудников
    if request.user.is_superuser or request.user.is_manager:
        # Менеджеры видят всех
        employees = Employee.objects.filter(
            is_active=True,
            is_superuser=False
        ).order_by('last_name', 'first_name')
    else:
        # Сотрудник видит только себя
        employees = Employee.objects.filter(
            id=request.user.id
        )
    # Фильтруем сотрудников по активности в выбранном месяце
    active_employees = []
    for employee in employees:
        if not employee.dismissal_date:
            active_employees.append(employee)
        else:
            dismissal = employee.dismissal_date
            # Уволен в этом месяце или позже — показываем
            if dismissal.year > year or (dismissal.year == year and dismissal.month >= month):
                active_employees.append(employee)

    employees = active_employees

    # Группируем сотрудников по основному участку
    grouped_employees = defaultdict(list)

    for employee in employees:
        primary_workstation = employee.workstation_assignments.filter(
            is_primary=True).first()
        if primary_workstation:
            workstation_name = primary_workstation.workstation.name
            workstation_id = primary_workstation.workstation.id
        else:
            workstation_name = "Без участка"
            workstation_id = 0

        grouped_employees[(workstation_id, workstation_name)].append(employee)

    # Сортируем группы
    def sort_key(item):
        ws_id, ws_name = item[0]
        if ws_id == 0:
            return (999, ws_name)
        return (ws_id, ws_name)

    sorted_groups = sorted(grouped_employees.items(), key=sort_key)

    # Собираем данные для каждой группы
    group_data = []
    for (ws_id, ws_name), employees_in_group in sorted_groups:
        employees_in_group = sorted(
            employees_in_group, key=lambda e: e.last_name)

        month_attendances = {}
        month_totals = {}
        for employee in employees_in_group:
            attendances = DailyAttendance.objects.filter(
                employee=employee,
                record_date__year=year,
                record_date__month=month
            )
            day_dict = {}
            total_hours = 0
            for att in attendances:
                day_dict[att.record_date.day] = att
                if att.is_present:
                    total_hours += att.actual_hours
            month_attendances[employee.id] = day_dict
            month_totals[employee.id] = total_hours

        employee_data = []
        for employee in employees_in_group:
            employee_data.append({
                'employee': employee,
                'dismissal_date': employee.dismissal_date,
            })

        group_data.append({
            'workstation_name': ws_name,
            'workstation_id': ws_id,
            'employees': employee_data,
            'month_attendances': month_attendances,
            'month_totals': month_totals,
        })

    return render(request, 'attendance/calendar.html', {
        'group_data': group_data,
        'days_in_month': days_in_month_list,
        'year': year,
        'month': month,
        'month_name': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
        'today': today,
        'can_edit': request.user.is_superuser,
    })


@login_required
@user_passes_test(is_manager)
def report_employee_hours(request):
    """Отчет по отработанным часам сотрудников"""
    from datetime import datetime
    from meta_app.workstations.models import Workstation
    from .models import MonthlyWorkNorm

    today = timezone.now().date()

    # Параметры фильтрации
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    workstation_id = request.GET.get('workstation')

    # Список участков для фильтра
    workstations = Workstation.objects.filter(is_active=True).order_by('name')

    # Получаем сотрудников
    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).order_by('last_name', 'first_name')

    # Фильтруем по дате увольнения
    active_employee_ids = []
    for emp in employees:
        if not emp.dismissal_date:
            active_employee_ids.append(emp.id)
        else:
            if emp.dismissal_date.year > year or (emp.dismissal_date.year == year and emp.dismissal_date.month >= month):
                active_employee_ids.append(emp.id)

    employees = Employee.objects.filter(id__in=active_employee_ids)

    # Фильтр по основному участку
    if workstation_id and workstation_id != 'all':
        try:
            ws = Workstation.objects.get(id=workstation_id)
            employees = employees.filter(
                workstation_assignments__workstation=ws,
                workstation_assignments__is_primary=True
            ).distinct()
        except Workstation.DoesNotExist:
            pass

    # Получаем норму часов за месяц
    try:
        norm = MonthlyWorkNorm.objects.get(year=year, month=month)
        hours_norm = norm.hours_norm
    except MonthlyWorkNorm.DoesNotExist:
        hours_norm = 0

    # Собираем данные по каждому сотруднику
    report_data = []
    for employee in employees:
        # Все записи за месяц (где был на работе)
        attendances = employee.attendances.filter(
            record_date__year=year,
            record_date__month=month,
            is_present=True
        )

        # Разделяем на рабочие дни и выходные
        work_attendances = attendances.filter(is_weekend_shift=False)
        weekend_attendances = attendances.filter(is_weekend_shift=True)

        # Количество дней
        work_days = work_attendances.count()
        weekend_works = weekend_attendances.count()
        total_days = work_days + weekend_works

        # Часы (рабочие и выходные)
        work_hours = sum(
            [att.actual_hours for att in work_attendances], Decimal('0'))
        weekend_hours = sum(
            [att.actual_hours for att in weekend_attendances], Decimal('0'))
        total_hours = work_hours + weekend_hours

        # Переработка ТОЛЬКО в рабочие дни (сверх нормы)
        overtime = Decimal('0')
        overtime_days = 0
        for att in work_attendances:
            day_norm = att.workstation.hours_per_day if att.workstation else Decimal(
                '8.0')
            if att.actual_hours > day_norm:
                overtime += att.actual_hours - day_norm
                overtime_days += 1

        # Процент от нормы (от общих часов, включая выходные)
        if hours_norm > 0 and total_hours > 0:
            persent = float(total_hours) / float(hours_norm) * 100
        else:
            persent = 0

        # Основной участок
        primary_workstation = employee.workstation_assignments.filter(
            is_primary=True).first()
        workstation_name = primary_workstation.workstation.name if primary_workstation else '—'

        # Среднее часов в рабочий день
        avg_hours = float(work_hours) / work_days if work_days > 0 else 0

        report_data.append({
            'employee': employee,
            'workstation': workstation_name,
            'work_days': work_days,                    # только рабочие дни
            'weekend_works': weekend_works,            # количество выходных дней
            'total_days': total_days,                  # всего дней
            'work_hours': float(work_hours),           # часы в рабочие дни
            'weekend_hours': float(weekend_hours),     # часы в выходные
            # всего часов (рабочие + выходные)
            'total_hours': float(total_hours),
            'norm_hours': float(hours_norm),           # норма за месяц
            # переработка (только рабочие дни)
            'overtime': float(overtime),
            'overtime_days': overtime_days,            # дни с переработкой
            'avg_hours': avg_hours,
            'attendances': attendances,
            # % от нормы (от общих часов)
            'persent': persent,
        })

    # Сортируем по фамилии сотрудника
    report_data.sort(key=lambda x: x['employee'].last_name)

    return render(request, 'attendance/report_hours.html', {
        'report_data': report_data,
        'year': year,
        'month': month,
        'month_name': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
        'workstations': workstations,
        'selected_workstation': workstation_id,
        'hours_norm': float(hours_norm),
        'current_year': today.year,
        'current_month': today.month,
    })

@login_required
@user_passes_test(is_manager)
def norm_list(request):
    """Список норм часов"""
    # Получаем все нормы
    all_norms = MonthlyWorkNorm.objects.all().order_by('-year', 'month')

    # Группируем по годам
    years = list(MonthlyWorkNorm.objects.values_list(
        'year', flat=True).distinct().order_by('-year'))
    if not years:
        years = [2026]

    # Строим таблицу данных
    months = [
        {'id': 1, 'name': 'Январь'},
        {'id': 2, 'name': 'Февраль'},
        {'id': 3, 'name': 'Март'},
        {'id': 4, 'name': 'Апрель'},
        {'id': 5, 'name': 'Май'},
        {'id': 6, 'name': 'Июнь'},
        {'id': 7, 'name': 'Июль'},
        {'id': 8, 'name': 'Август'},
        {'id': 9, 'name': 'Сентябрь'},
        {'id': 10, 'name': 'Октябрь'},
        {'id': 11, 'name': 'Ноябрь'},
        {'id': 12, 'name': 'Декабрь'},
    ]

    # Создаём данные для таблицы
    table_data = []
    for month in months:
        row = {
            'month': month['name'],
            'month_id': month['id'],
            'norms': {},
        }
        for year in years:
            norm = MonthlyWorkNorm.objects.filter(
                year=year, month=month['id']).first()
            row['norms'][year] = norm
        table_data.append(row)

    return render(request, 'attendance/norm_list.html', {
        'table_data': table_data,
        'years': years,
    })


@login_required
@user_passes_test(is_manager)
def norm_edit(request, norm_id=None):
    """Редактирование или создание нормы"""
    if norm_id:
        norm = get_object_or_404(MonthlyWorkNorm, id=norm_id)
    else:
        norm = None

    if request.method == 'POST':
        form = MonthlyWorkNormForm(request.POST, instance=norm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Норма часов сохранена!')
            return redirect('dashboard:norm_list')
    else:
        form = MonthlyWorkNormForm(instance=norm)

    return render(request, 'attendance/norm_edit.html', {
        'form': form,
        'norm': norm,
    })


@login_required
@user_passes_test(is_manager)
def norm_delete(request, norm_id):
    """Удаление нормы"""
    norm = get_object_or_404(MonthlyWorkNorm, id=norm_id)
    year = norm.year
    month = norm.month
    norm.delete()
    messages.success(request, f'Норма за {month}.{year} удалена!')
    return redirect('dashboard:norm_list')


@login_required
@user_passes_test(is_manager)
def norm_fill(request):
    """Быстрое заполнение норм для всех месяцев года"""
    if request.method == 'POST':
        year = request.POST.get('year')
        hours = request.POST.get('hours')

        if not year or not hours:
            messages.error(request, 'Укажите год и норму часов')
            return redirect('dashboard:norm_list')

        try:
            year = int(year)
            hours = float(hours)
        except ValueError:
            messages.error(request, 'Некорректные данные')
            return redirect('dashboard:norm_list')

        created_count = 0
        for month in range(1, 13):
            obj, created = MonthlyWorkNorm.objects.get_or_create(
                year=year,
                month=month,
                defaults={'hours_norm': hours}
            )
            if created:
                created_count += 1

        messages.success(
            request, f'Создано {created_count} норм для {year} года')
        return redirect('dashboard:norm_list')

    return redirect('dashboard:norm_list')


@login_required
@user_passes_test(is_manager)
def norm_bulk_edit(request):
    """Массовое редактирование норм часов за год"""
    from .forms import MonthlyWorkNormBulkForm

    # Определяем год по умолчанию
    default_year = 2026

    # Если есть GET параметр year — используем его
    if request.GET.get('year'):
        default_year = int(request.GET.get('year'))
    elif MonthlyWorkNorm.objects.exists():
        default_year = MonthlyWorkNorm.objects.order_by('-year').first().year

    if request.method == 'POST':
        # Получаем год из POST
        year = int(request.POST.get('year', default_year))

        # Создаём форму с переданными данными
        form = MonthlyWorkNormBulkForm(request.POST, year=year)

        if form.is_valid():
            created_count = 0
            updated_count = 0

            # Сохраняем каждый месяц
            for month in range(1, 13):
                field_name = f'month_{month}'
                hours = form.cleaned_data.get(field_name)

                if hours is not None and hours != '':
                    norm, created = MonthlyWorkNorm.objects.update_or_create(
                        year=year,
                        month=month,
                        defaults={'hours_norm': hours}
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            messages.success(
                request,
                f'Нормы для {year} года сохранены! '
                f'Создано: {created_count}, обновлено: {updated_count}'
            )
            return redirect(f'{request.path}?year={year}')
    else:
        # GET запрос — показываем форму с выбранным годом
        form = MonthlyWorkNormBulkForm(year=default_year)

    # Получаем данные для отображения текущего года
    month_data = []
    for month in range(1, 13):
        norm = MonthlyWorkNorm.objects.filter(
            year=default_year, month=month).first()
        month_data.append({
            'month': month,
            'name': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                     'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
            'hours': norm.hours_norm if norm else None,
        })

    return render(request, 'attendance/norm_bulk_edit.html', {
        'form': form,
        'year': default_year,
        'month_data': month_data,
        'months': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    })


@login_required
def vacation_create(request):
    """Создание заявки на отпуск"""
    if request.method == 'POST':
        form = VacationRequestForm(request.POST)
        if form.is_valid():
            vacation = form.save(commit=False)
            vacation.employee = request.user
            vacation.status = 'pending'
            vacation.save()
            messages.success(request, 'Заявка на отпуск отправлена на согласование')
            return redirect('dashboard:vacation_list')
    else:
        form = VacationRequestForm()
        
    return render(request, 'attendance/vacation_create.html', {
        'form': form,
    })    
    

@login_required
def vacation_list(request):
    """Список заявок на отпуск"""
    # Для менеджера - все заявки, для сотрудника - только свои.
    if request.user.is_superuser or request.user.is_manager:
        vacations = VacationRequest.objects.all().order_by('-created_at')
    else:
        vacations = VacationRequest.objects.filter(employee=request.user).order_by('-created_at')
        
    return render(request, 'attendance/vacation_list.html', {
                  'vacations': vacations,
                  'is_manager': request.user.is_superuser or request.user.is_manager,
    })
    

@login_required
@user_passes_test(is_manager)
def vacation_process(request, vacation_id):
    """Обработка заявки на отпуск (только для менеджеров)"""
    vacation = get_object_or_404(VacationRequest, id=vacation_id)
    
    if request.method == 'POST':
        form = VacationRequestProcessForm(request.POST, instance=vacation)
        if form.is_valid():
            vacation = form.save(commit=False)
            vacation.processed_by = request.user
            vacation.processed_at = timezone.now()
            vacation.save()
            
            if vacation.status == 'approved':
                from .models import DailyAttendance
                for date in vacation.get_date():
                    DailyAttendance.objects.get_or_create(
                        employee=vacation.employee,
                        record_date=date,
                        defaults={
                            'workstation': None,
                            'status': 'vacation',
                            'is_present': False,
                            'note': f'Отпуск (одобрен {request.user.short_name})',
                        }
                    )
                messages.success(request, f'Отпуск для {vacation.employee.short_name} подтвержден!')
            elif vacation.status == 'rejected':
                messages.warning(request, f'Заявка на отпуск для {vacation.employee.short_name} отклонена.')
                
            return redirect('dashboard:vacation_list')
    
    else:
        form = VacationRequestProcessForm(instance=vacation)
        
    return render(request, 'attendance/vacation_process.html', {
        'form': form,
        'vacation': vacation
    })
    
    
@login_required
def vacation_cancel(request, vacation_id):
    """Отмена заявки на отпуск (только для автора)"""
    vacation = get_object_or_404(VacationRequest, id=vacation_id, employee=request.user)
    
    if vacation.status in ['approved', 'rejected']:
        messages.error(request, 'Нельзя отменить уже обработанную заявку.')
        return redirect('dashboard:vacation_list')
    
    vacation.status = 'cancelled'
    vacation.save()
    messages.success(request, 'Заявка на отпуск отмененаю')
    return redirect('dashboard:vacation_list')
