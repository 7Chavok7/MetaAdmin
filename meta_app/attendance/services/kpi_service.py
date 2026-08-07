# meta_app/attendance/services/kpi_service.py

from decimal import Decimal
from meta_app.attendance.models import KPI, EmployeeKPIValue, DailyAttendance


class KPIService:
    
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
        
        # 🔥 Упрощенная логика
        if kpi.type == 'no_absence':
            # Нет пропусков ЛЮБОГО типа (прогул, больничный, отпуск)
            has_absence = attendances.filter(
                status__in=['absent', 'sick', 'vacation']
            ).exists()
            is_completed = not has_absence
            
        elif kpi.type == 'has_skills':
            # Есть навыки
            skills = employee.employee_skills.select_related('skill').all()
            is_completed = skills.exists()
            
        elif kpi.type == 'overtime':
            # Была переработка
            has_overtime = attendances.filter(overtime_hours__gt=0).exists()
            is_completed = has_overtime
            
        elif kpi.type == 'clean_workplace':
            # Чистое рабочее место (пока заглушка)
            is_completed = True
            
        else:
            # Пользовательский KPI
            is_completed = True
        
        # Рассчитываем бонус
        bonus = Decimal('0')
        if is_completed:
            # Фиксированный бонус
            bonus += Decimal(str(kpi.bonus_amount or 0))
            
            # Процент от оклада
            if kpi.bonus_percent:
                base_salary = Decimal(str(employee.base_salary or 0))
                bonus += base_salary * Decimal(str(kpi.bonus_percent / 100))
            
            # Бонус за навыки
            if kpi.type == 'has_skills' and kpi.skill_price:
                skills_count = employee.employee_skills.count()
                bonus += Decimal(str(kpi.skill_price)) * skills_count
        
        return is_completed, bonus