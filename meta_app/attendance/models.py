from django.db import models
from django.utils import timezone
from meta_app.employees.models import Employee
from meta_app.workstations.models import Workstation


class DailyAttendance(models.Model):
    """Дневная запись о работе сотрудника"""

    STATUS_CHOICES = [
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('weekend', 'Выходной'),
        ('sick', 'Больничный'),
        ('vacation', 'Отпуск'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Сотрудник'
    )
    record_date = models.DateField(
        default=timezone.now,
        verbose_name='Дата'
    )
    workstation = models.ForeignKey(
        Workstation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Участок'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name='Статус'
    )
    is_present = models.BooleanField(
        default=True,
        verbose_name='Был на работе'
    )
    is_weekend_shift = models.BooleanField(
        default=False,
        verbose_name='Работа в выходной'
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Время окончания'
    )
    hours_norm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.0,
        verbose_name='Норма часов'
    )
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Переработка (часов)'
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Фактические часы'
    )
    note = models.TextField(
        blank=True,
        verbose_name='Примечание'
    )

    # Системные поля
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_attendances',
        verbose_name='Кто создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_attendances',
        verbose_name='Кто редактировал'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата редактирования'
    )

    class Meta:
        verbose_name = 'Запись о работе'
        verbose_name_plural = 'Записи о работе'
        unique_together = ['employee', 
                           'record_date']
        ordering = ['-record_date',
                    'employee__last_name', 
                    'employee__first_name']

    def __str__(self):
        return f"{self.employee.full_name} - {self.record_date}"


    def save(self, *args, **kwargs):
        """Автоматически рассчитываем часы при сохранении"""

        # 1. Обновляем is_present в зависимости от статуса
        if self.status in ['absent', 'weekend', 'sick', 'vacation']:
            self.is_present = False
        else:
            self.is_present = True

        # 2. Рассчитываем часы
        if self.is_present and self.start_time and self.end_time:
            start = self.start_time
            end = self.end_time

            start_minutes = start.hour * 60 + start.minute
            end_minutes = end.hour * 60 + end.minute

            if end_minutes < start_minutes:
                end_minutes += 24 * 60

            diff_minutes = end_minutes - start_minutes

            if diff_minutes > 6 * 60:
                diff_minutes -= 60

            hours = diff_minutes / 60
            self.actual_hours = round(hours, 2) + float(self.overtime_hours or 0)
        else:
            self.actual_hours = 0

        super().save(*args, **kwargs)


class MonthlyWorkNorm(models.Model):
    """Нормы рабочего времени"""
    year = models.IntegerField(verbose_name='Год')
    month = models.IntegerField(verbose_name='Месяц')
    hours_norm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='Норма часов (40-чвсовая неделя)'
    )
    
    class Meta:
        verbose_name = 'Норма рабочего времени'
        verbose_name_plural = 'Нормы рабочего времени'
        unique_together = ['year', 'month']
        ordering = ['-year', 'month']
        
    def __str__(self):
        return f"{self.month}/{self.year}: {self.hours_norm}"