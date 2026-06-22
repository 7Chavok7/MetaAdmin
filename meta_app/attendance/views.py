from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from meta_app.employees.models import Employee
from meta_app.workstations.models import EmployeeWorkstation
from .models import DailyAttendance
from .forms import AttendanceForm


def is_manager(user):
    return user.is_authenticated and (user.is_superuser or user.is_manager)


@login_required
@user_passes_test(is_manager)
def attendance_today(request):
    """Главная страница учета времени на сегодня"""
    today = timezone.now().date()

    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False  # ← исключаем суперпользователей
    ).order_by('last_name', 'first_name')

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
        'can_edit': request.user.is_superuser,
    })


@login_required
@user_passes_test(is_manager)
def attendance_create(request, employee_id):
    """Создание записи за любой день"""
    employee = get_object_or_404(Employee, id=employee_id)

    # Если сотрудник - суперпользователь и текущий пользователь не суперпользователь
    if employee.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Нельзя создавать записи для администратора')
        return redirect('dashboard:home')

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
            return redirect('dashboard:attendance_today')
    else:
        # Получаем дату из GET-параметра
        date_param = request.GET.get('date')

        # Если дата передана - используем её, иначе сегодня
        if date_param:
            try:
                record_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                # Преобразуем в строку для initial
                record_date_str = date_param  # уже в правильном формате
            except ValueError:
                record_date = timezone.now().date()
                record_date_str = record_date.strftime('%Y-%m-%d')
        else:
            record_date = timezone.now().date()
            record_date_str = record_date.strftime('%Y-%m-%d')

        next_url = request.GET.get('next')

        # Предзаполняем участок, если есть основной
        default_workstation = None
        primary_assignment = employee.workstation_assignments.filter(
            is_primary=True).first()
        if primary_assignment:
            default_workstation = primary_assignment.workstation

        # Создаем форму с initial данными
        initial_data = {
            'record_date': record_date_str,  # ← передаем строку!
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

    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на редактирование!')
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
            return redirect('dashboard:attendance_today')
    else:
        # Создаем форму с existing данными
        form = AttendanceForm(instance=attendance)

        # Убеждаемся, что дата правильно отображается
        if attendance.record_date:
            # Передаем дату в правильном формате
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

    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на удаление!')
        return redirect('dashboard:attendance_today')

    employee_name = attendance.employee.full_name
    attendance.delete()
    messages.success(request, f'Запись для {employee_name} удалена!')
    return redirect('dashboard:attendance_today')


@login_required
@user_passes_test(is_manager)
def attendance_all(request):
    """Список всех записей с фильтром"""
    employee_id = request.GET.get('employee')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Базовый запрос (исключая суперпользователей)
    attendances = DailyAttendance.objects.filter(
        employee__is_superuser=False  # ← исключаем суперпользователей
    ).order_by('-record_date', 'employee__last_name')

    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    if date_from:
        attendances = attendances.filter(record_date__gte=date_from)
    if date_to:
        attendances = attendances.filter(record_date__lte=date_to)

    employees = Employee.objects.filter(
        is_active=True).order_by('last_name', 'first_name')

    return render(request, 'attendance/all.html', {
        'attendances': attendances,
        'employees': employees,
        'selected_employee': employee_id,
        'date_from': date_from,
        'date_to': date_to,
        'can_edit': request.user.is_superuser,
    })


@login_required
@user_passes_test(is_manager)
def attendance_calendar(request, year=None, month=None):
    """Календарь посещаемости в виде таблицы"""
    from calendar import monthrange
    from datetime import date

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

    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).order_by('last_name', 'first_name')

    month_attendances = {}
    month_totals = {}

    for employee in employees:
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

    return render(request, 'attendance/calendar.html', {
        'employees': employees,
        'month_attendances': month_attendances,
        'month_totals': month_totals,
        'days_in_month': days_in_month_list,
        'year': year,
        'month': month,
        'month_name': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month - 1],
        'today': today,
        'can_edit': request.user.is_superuser,
    })
