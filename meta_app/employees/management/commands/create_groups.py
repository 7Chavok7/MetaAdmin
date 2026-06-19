from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from meta_app.employees.models import Employee


class Command(BaseCommand):
    help = 'Создает группы и назначает права'

    def handle(self, *args, **options):
        # Получаем ContentType для модели Employee
        employee_content_type = ContentType.objects.get_for_model(Employee)

        # Получаем все права для модели Employee
        all_permissions = Permission.objects.filter(
            content_type=employee_content_type)

        # --- 1. Группа "Руководители" (полный доступ) ---
        managers_group, created = Group.objects.get_or_create(
            name='Руководители')
        if created:
            self.stdout.write('✅ Создана группа "Руководители"')

        # Даем все права
        managers_group.permissions.set(all_permissions)
        self.stdout.write('   - Все права назначены')

        # --- 2. Группа "Заместители" (только просмотр) ---
        deputies_group, created = Group.objects.get_or_create(
            name='Заместители')
        if created:
            self.stdout.write('✅ Создана группа "Заместители"')

        # Даем только права на просмотр
        view_permissions = Permission.objects.filter(
            content_type=employee_content_type,
            codename__in=['view_employee', 'view_skill', 'view_employeeskill']
        )
        deputies_group.permissions.set(view_permissions)
        self.stdout.write('   - Права на просмотр назначены')

        # --- 3. Группа "Сотрудники" (без доступа к админке) ---
        employees_group, created = Group.objects.get_or_create(
            name='Сотрудники')
        if created:
            self.stdout.write('✅ Создана группа "Сотрудники"')

        # Даем минимальные права (только просмотр себя)
        self_permission = Permission.objects.filter(
            content_type=employee_content_type,
            codename='view_employee'
        )
        employees_group.permissions.set(self_permission)
        self.stdout.write('   - Права на просмотр себя назначены')

        self.stdout.write(self.style.SUCCESS('🎉 Группы и права созданы!'))
