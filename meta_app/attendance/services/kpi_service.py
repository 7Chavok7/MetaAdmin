# meta_app/attendance/services/kpi_service.py

from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from meta_app.attendance.models import KPI, DailyAttendance, SalaryRecord
import calendar


class KPIService:
    
    @staticmethod
    def get_workdays_in_month(employee, year, month):
        """
        Получить количество рабочих дней в месяце для сотрудника
        Учитывает график работы сотрудника (5/2 или 2/2)
        """
        # Получаем основное подразделение сотрудника
        primary_assignment = employee.workstation_assignments.filter(is_primary=True).first()
        
        if not primary_assignment:
            # Если нет основного участка — считаем стандартные 5/2
            workdays = 0
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                date = timezone.datetime(year, month, day).date()
                if date.weekday() < 5:  # Пн-Пт
                    workdays += 1
            return workdays
        
        workstation = primary_assignment.workstation
        schedule_type = workstation.schedule_type
        
        if schedule_type == '5_2':
            # 5/2: считаем рабочие дни (Пн-Пт)
            workdays = 0
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                date = timezone.datetime(year, month, day).date()
                if date.weekday() < 5:
                    workdays += 1
            return workdays
        
        elif schedule_type == '2_2':
            # 2/2: примерно половина дней
            # TODO: более точная логика для 2/2
            total_days = calendar.monthrange(year, month)[1]
            return total_days // 2
        
        return 20  # По умолчанию
    
    
    @staticmethod
    def calculate_kpi_for_employee(employee, year, month, kpi):
        """Рассчитать KPI по его типу"""
        
        if not kpi.is_active:
            return False, Decimal('0')
        
        # Получаем данные сотрудника за месяц
        attendances = DailyAttendance.objects.filter(
            employee=employee,
            record_date__year=year,
            record_date__month=month
        )
        
        # ============================================
        # KPI: Нет пропусков
        # ============================================
        if kpi.type == 'no_absence':
            total_workdays = KPIService.get_workdays_in_month(employee, year, month)
            present_days = attendances.filter(status='present').count()
            absence_days = attendances.filter(
                status__in=['absent', 'sick', 'vacation']
            ).count()
            
            is_completed = (
                total_workdays > 0 and 
                present_days == total_workdays and 
                absence_days == 0
            )
            bonus = Decimal('0')
            
        # ============================================
        # KPI: Есть навыки
        # ============================================
        elif kpi.type == 'has_skills':
            skills = employee.employee_skills.select_related('skill').all()
            skill_count = skills.count()
            
            # 1 навык → входит в оклад (бонус 0)
            # 2+ навыков → бонус за каждый навык сверх 1-го
            is_completed = True
            
            if skill_count >= 2:
                bonus_skills = skill_count - 1  # Навыки сверх 1-го
                bonus = Decimal(str(kpi.skill_price)) * bonus_skills
            else:
                bonus = Decimal('0')
                
        # ============================================
        # KPI: Была переработка
        # ============================================
        elif kpi.type == 'overtime':
            has_overtime = attendances.filter(
                overtime_hours__gt=0,
                status='present'
            ).exists()
            is_completed = has_overtime
            bonus = Decimal('0')
            
        # ============================================
        # KPI: Чистое рабочее место
        # ============================================
        elif kpi.type == 'clean_workplace':
            is_completed = True
            bonus = Decimal('0')
            
        # ============================================
        # Пользовательский KPI
        # ============================================
        else:
            is_completed = True
            bonus = Decimal('0')
        
        # Если KPI выполнен, добавляем фиксированный бонус и процент (НО НЕ НАВЫКИ!)
        if is_completed:
            # Фиксированный бонус
            bonus += Decimal(str(kpi.bonus_amount or 0))
            
            # Процент от оклада
            if kpi.bonus_percent:
                base_salary = Decimal(str(employee.base_salary or 0))
                bonus += base_salary * Decimal(str(kpi.bonus_percent / 100))
        
        return is_completed, bonus
    
    @staticmethod
    def calculate_all_kpis_for_month(employee, year, month):
        """Рассчитать все KPI для сотрудника за месяц"""
        
        results = []
        kpis = KPI.objects.filter(is_active=True)
        
        for kpi in kpis:
            is_completed, bonus = KPIService.calculate_kpi_for_employee(
                employee, year, month, kpi
            )
            
            results.append({
                'kpi': kpi,
                'is_completed': is_completed,
                'bonus': bonus,
            })
        
        return results
    
    @staticmethod
    def calculate_and_save_salary(employee, year, month, calculated_by=None):
        """Рассчитать и сохранить зарплату сотрудника за месяц"""
        
        # Рассчитываем KPI
        kpi_results = KPIService.calculate_all_kpis_for_month(employee, year, month)
        
        base_salary = Decimal(str(employee.base_salary or 0))
        total_bonus = sum([Decimal(str(r['bonus'])) for r in kpi_results], Decimal('0'))
        total_salary = base_salary + total_bonus
        
        # Детали KPI для отладки
        kpi_details = {}
        for r in kpi_results:
            kpi_details[r['kpi'].name] = {
                'completed': r['is_completed'],
                'bonus': float(r['bonus'])
            }
        
        # Сохраняем запись
        salary_record, created = SalaryRecord.objects.update_or_create(
            employee=employee,
            year=year,
            month=month,
            defaults={
                'base_salary': base_salary,
                'kpi_bonus': total_bonus,
                'total_salary': total_salary,
                'kpi_details': kpi_details,
                'is_calculated': True,
                'calculated_at': timezone.now(),
                'calculated_by': calculated_by,
            }
        )
        
        return salary_record
    
    @staticmethod
    def calculate_all_salaries(year, month, calculated_by=None):
        """Рассчитать зарплаты всех сотрудников за месяц"""
        from meta_app.employees.models import Employee
        
        employees = Employee.objects.filter(is_active=True, is_superuser=False)
        results = []
        
        for employee in employees:
            salary_record = KPIService.calculate_and_save_salary(
                employee, year, month, calculated_by
            )
            results.append(salary_record)
        
        return results