from django.db import models


class Department(models.Model):
    """Подразделение (цехб отдел)"""
    
    name = models.CharField(
        max_length=255,
        verbose_name='Название подразделения'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Код подразделения'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительское подразделение'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )
    
    # Системные поля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )
    
    class Meta:
        verbose_name = 'Подразделение',
        verbose_name_plural = 'Подразделения'
        ordering = ['order', 'name']
        
    def __str__(self):
        if self.parent:
            return f"{self.parent.name}-{self.name}"
        return self.name
    
    def full_path(self):
        """Полный путь к подразделению"""
        if self.parent:
            return f"{self.parent.full_path}-{self.name}"
        return self.name

class Workstation(models.Model):
    """Участок производства"""

    SCHEDULE_TYPES = [
        ('5_2', '5/2 (Пн-Пт)'),
        ('2_2', '2/2 (сменный)'),
    ]
    
    # связь с подразделением
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='workstations',
        verbose_name='Подразделение',
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Название участка'
    )
    short_name = models.CharField(
        max_length=20,
        verbose_name='Сокращение'
    )
    schedule_type = models.CharField(
        max_length=10,
        choices=SCHEDULE_TYPES,
        default='5_2',
        verbose_name='Режим работы'
    )
    work_start = models.TimeField(
        default='08:00',
        verbose_name='Время начала смены'
    )
    work_end = models.TimeField(
        default='17:00',
        verbose_name='Время окончания смены'
    )
    hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=8.0,
        verbose_name='Часов в день'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Цвет для отображения'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    # Системные поля (аудит)
    created_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_workstations',
        verbose_name='Кто создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_workstations',
        verbose_name='Кто редактировал'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата редактирования'
    )

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'
        ordering = ['department__name', 'name']

    def __str__(self):
        if self.department:
            return f"{self.department.name}-{self.name} ({self.short_name})"
        return f"{self.name} ({self.short_name})"

    @property
    def full_name(self):
        if self.department:
            return f"{self.department.name} → {self.name} ({self.short_name})"
        return f"{self.name} ({self.short_name})"
    
    @property
    def department_name(self):
        """Короткое название подразделения"""
        return self.department.name if self.department else 'Без подразделения'


class EmployeeWorkstation(models.Model):
    """Привязка сотрудника к участку"""

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='workstation_assignments',
        verbose_name='Сотрудник'
    )
    workstation = models.ForeignKey(
        Workstation,
        on_delete=models.CASCADE,
        related_name='employee_assignments',
        verbose_name='Участок'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Основное место работы'
    )
    assigned_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата назначения'
    )
    note = models.TextField(
        blank=True,
        verbose_name='Примечание'
    )

    # Системные поля (аудит)
    created_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments',
        verbose_name='Кто создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_assignments',
        verbose_name='Кто редактировал'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата редактирования'
    )

    class Meta:
        verbose_name = 'Назначение на участок'
        verbose_name_plural = 'Назначения на участки'
        unique_together = ['employee', 'workstation']
        ordering = ['employee__last_name', 'workstation__name']

    def __str__(self):
        return f"{self.employee.full_name} → {self.workstation.name}"
