# meta_app/attendance/management/commands/calculate_salaries.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from meta_app.employees.models import Employee
from meta_app.attendance.services.kpi_service import KPIService


class Command(BaseCommand):
    help = 'Рассчитать зарплаты сотрудников за месяц'

    def handle(self, *args, **options):
        year = timezone.now().year
        month = timezone.now().month
        
        employees = Employee.objects.filter(is_active=True, is_superuser=False)
        
        for employee in employees:
            base_salary = float(employee.base_salary or 0)
            total_bonus = 0
            completed_kpis = []
            failed_kpis = []
            
            # Рассчитываем все KPI
            kpi_results = KPIService.calculate_all_kpis_for_month(employee, year, month)
            
            for result in kpi_results:
                total_bonus += float(result['bonus'])
                if result['is_completed']:
                    completed_kpis.append(result['kpi'].name)
                else:
                    failed_kpis.append(result['kpi'].name)
            
            total_salary = base_salary + total_bonus
            
            self.stdout.write(
                f"{employee.full_name}: "
                f"Оклад={base_salary:.2f}, "
                f"Бонус={total_bonus:.2f}, "
                f"Итого={total_salary:.2f}"
            )
            if completed_kpis:
                self.stdout.write(f"  ✅ Выполненные KPI: {', '.join(completed_kpis)}")
            if failed_kpis:
                self.stdout.write(f"  ❌ Невыполненные KPI: {', '.join(failed_kpis)}")