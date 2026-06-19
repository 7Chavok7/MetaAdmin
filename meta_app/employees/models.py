from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Employee(AbstractUser):
    """Модель сотрудника с анкетными данными"""

    # Убираем ненужные поля от AbstractUser
    username = None
    first_name = None
    last_name = None
    email = None
    groups = None
    user_permissions = None

    # Базовые поля
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Табельный номер'
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

    # Трудовой стаж (предыдущие места работы)
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

    # Дата приема и увольнения
    hire_date = models.DateField(
        default=timezone.now,
        verbose_name='Дата приема'
    )
    dismissal_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата увольнения'
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    @property
    def full_name(self):
        """Полное имя"""
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()
