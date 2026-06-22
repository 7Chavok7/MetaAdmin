from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from meta_app.employees.models import Employee
from meta_app.attendance.models import DailyAttendance


class Command(BaseCommand):
    help = 'Создает записи на выходные дни для всех сотрудников'

    def handle(self, *args, **options):
        today = timezone.now().date()

        # За последние 30 дней
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=7)  # На неделю вперед

        employees = Employee.objects.filter(is_active=True, is_superuser=False)

        created_count = 0
        skipped_count = 0
        current_date = start_date

        while current_date <= end_date:
            # Проверяем, выходной ли день
            if current_date.weekday() >= 5:  # Сб или Вс
                for employee in employees:
                    # Проверяем, есть ли уже запись
                    existing = DailyAttendance.objects.filter(
                        employee=employee,
                        record_date=current_date
                    ).exists()

                    if not existing:
                        # Создаем запись "Выходной"
                        DailyAttendance.objects.create(
                            employee=employee,
                            record_date=current_date,
                            status='weekend',
                            is_present=False,
                            hours_norm=0,
                            actual_hours=0,
                            note='Автоматически созданная запись (выходной)'
                        )
                        created_count += 1
                    else:
                        skipped_count += 1

            current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Создано {created_count} записей для выходных дней')
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ Пропущено {skipped_count} записей (уже существуют)')
            )
