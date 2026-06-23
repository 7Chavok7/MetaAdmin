from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from meta_app.employees.models import Employee
from meta_app.workstations.models import Workstation, EmployeeWorkstation
from meta_app.attendance.models import DailyAttendance


class Command(BaseCommand):
    help = 'Настройка прав доступа'

    def handle(self, *args, **options):
        # Создаем группы
        managers_group, _ = Group.objects.get_or_create(name='Менеджеры')
        employees_group, _ = Group.objects.get_or_create(name='Сотрудники')

        # Права для модели Employee
        employee_ct = ContentType.objects.get_for_model(Employee)
        employee_perms = Permission.objects.filter(content_type=employee_ct)

        # Менеджеры: все права
        managers_group.permissions.set(employee_perms)

        # Сотрудники: только просмотр
        view_perm = Permission.objects.get(
            content_type=employee_ct,
            codename='view_employee'
        )
        employees_group.permissions.set([view_perm])

        # Права для Workstation
        workstation_ct = ContentType.objects.get_for_model(Workstation)
        workstation_perms = Permission.objects.filter(
            content_type=workstation_ct)
        managers_group.permissions.add(*workstation_perms)

        # Права для EmployeeWorkstation
        assignment_ct = ContentType.objects.get_for_model(EmployeeWorkstation)
        assignment_perms = Permission.objects.filter(
            content_type=assignment_ct)
        managers_group.permissions.add(*assignment_perms)

        # Права для DailyAttendance
        attendance_ct = ContentType.objects.get_for_model(DailyAttendance)
        attendance_perms = Permission.objects.filter(
            content_type=attendance_ct)
        managers_group.permissions.add(*attendance_perms)

        self.stdout.write(self.style.SUCCESS('✅ Права доступа настроены!'))
