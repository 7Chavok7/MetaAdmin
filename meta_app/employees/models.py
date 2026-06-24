from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager


class EmployeeManager(BaseUserManager):
    """Кастомный менеджер для модели Employee"""

    def create_user(self, login, employee_id, last_name, first_name, birth_date, hire_date, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not login:
            raise ValueError('Логин обязателен')
        if not employee_id:
            raise ValueError('Табельный номер обязателен')
        if not last_name:
            raise ValueError('Фамилия обязательна')
        if not first_name:
            raise ValueError('Имя обязательно')
        if not birth_date:
            raise ValueError('Дата рождения обязательна')
        if not hire_date:
            raise ValueError('Дата приема обязательна')

        user = self.model(
            login=login,
            employee_id=employee_id,
            last_name=last_name,
            first_name=first_name,
            birth_date=birth_date,
            hire_date=hire_date,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, employee_id, last_name, first_name, birth_date, hire_date, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(login, employee_id, last_name, first_name, birth_date, hire_date, password, **extra_fields)


class Employee(AbstractUser):
    """Модель сотрудника с анкетными данными"""
    
    objects = EmployeeManager()

    # Убираем ненужные поля от AbstractUser
    username = None
    first_name = None
    last_name = None
    email = None
    groups = None
    user_permissions = None

    # Поля для аутентификации
    login = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин для входа'
    )

    # Табельный номер (отдельное поле)
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Табельный номер'
    )

    card_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Номер карточки'
    )
    
    

    is_active = models.BooleanField(
        default=True,
        verbose_name='Работает'
    )
    is_manager = models.BooleanField(
        default=False,
        verbose_name='Может редактировать данные'
    )

    # Личные данные
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    patronymic = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Отчество'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    phone_number = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )
    photo = models.ImageField(
        upload_to='employees/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )

    # Адреса
    registration_address = models.TextField(
        blank=True,
        verbose_name='Место регистрации'
    )
    residence_address = models.TextField(
        blank=True,
        verbose_name='Место проживания'
    )

    # Семейное положение
    MARITAL_STATUS_CHOICES = [
        ('single', 'Холост/Не замужем'),
        ('married', 'В браке'),
        ('divorced', 'Разведен(а)'),
        ('widowed', 'Вдовец/Вдова'),
    ]
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        verbose_name='Семейное положение'
    )
    has_children = models.BooleanField(
        default=False,
        verbose_name='Есть дети'
    )
    children_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Количество детей'
    )

    # Военная обязанность
    MILITARY_STATUS_CHOICES = [
        ('liable', 'Военнообязанный'),
        ('not_liable', 'Не военнообязанный'),
        ('served', 'Отслужил'),
        ('exempt', 'Освобожден'),
    ]
    military_status = models.CharField(
        max_length=20,
        choices=MILITARY_STATUS_CHOICES,
        blank=True,
        verbose_name='Военная обязанность'
    )

    # Образование
    education_specialty = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Специальность по образованию'
    )
    education_institution = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Где учился'
    )
    education_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Год окончания'
    )

    # Трудовой стаж
    previous_work_1 = models.TextField(
        blank=True,
        verbose_name='Предыдущее место работы 1'
    )
    previous_work_2 = models.TextField(
        blank=True,
        verbose_name='Предыдущее место работы 2'
    )
    previous_work_3 = models.TextField(
        blank=True,
        verbose_name='Предыдущее место работы 3'
    )

    # Даты
    hire_date = models.DateField(
        default=timezone.now,
        verbose_name='Дата приема'
    )
    dismissal_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата увольнения'
    )

    # Системные поля (аудит)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees',
        verbose_name='Кто создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_employees',
        verbose_name='Кто редактировал'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата редактирования'
    )

    # Поле для аутентификации (вход по логину)
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['employee_id', 'last_name',
                       'first_name', 'birth_date', 'hire_date']
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='employee_set',
        blank=True,
        verbose_name='Группы'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='employee_set',
        blank=True,
        verbose_name='Права доступа'
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического заполнения аудита"""
        if not self.pk:
            if hasattr(self, '_created_by_user'):
                self.created_by = self._created_by_user

        if hasattr(self, '_updated_by_user'):
            self.updated_by = self._updated_by_user

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()


class Skill(models.Model):
    """Модель навыка/квалификации"""

    CATEGORY_CHOICES = [
        ('production', 'Производство'),
        ('warehouse', 'Склад'),
        ('office', 'Офис'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название навыка'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Категория'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class EmployeeSkill(models.Model):
    """Связь сотрудника с навыками (квалификация)"""

    LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('middle', 'Средний'),
        ('expert', 'Эксперт'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='employee_skills',
        verbose_name='Сотрудник'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='skill_employees',
        verbose_name='Навык'
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='middle',
        verbose_name='Уровень'
    )
    certified_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата получения'
    )
    note = models.TextField(
        blank=True,
        verbose_name='Примечание'
    )

    class Meta:
        verbose_name = 'Квалификация сотрудника'
        verbose_name_plural = 'Квалификации сотрудников'
        unique_together = ['employee', 'skill']

    def __str__(self):
        return f"{self.employee.full_name} - {self.skill.name} ({self.get_level_display()})"
