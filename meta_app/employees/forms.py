from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """Форма для редактирования сотрудника"""

    class Meta:
        model = Employee
        fields = [
            'last_name',
            'first_name',
            'patronymic',
            'birth_date',
            'photo',
            'registration_address',
            'residence_address',
            'marital_status',
            'has_children',
            'children_count',
            'military_status',
            'education_specialty',
            'education_institution',
            'education_year',
            'previous_work_1',
            'previous_work_2',
            'previous_work_3',
            'hire_date',
            'dismissal_date',
            'is_active',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'dismissal_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_address': forms.Textarea(attrs={'rows': 3}),
            'residence_address': forms.Textarea(attrs={'rows': 3}),
            'previous_work_1': forms.Textarea(attrs={'rows': 2}),
            'previous_work_2': forms.Textarea(attrs={'rows': 2}),
            'previous_work_3': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'birth_date': 'Дата рождения',
            'photo': 'Фото',
            'registration_address': 'Место регистрации',
            'residence_address': 'Место проживания',
            'marital_status': 'Семейное положение',
            'has_children': 'Есть дети',
            'children_count': 'Количество детей',
            'military_status': 'Военная обязанность',
            'education_specialty': 'Специальность по образованию',
            'education_institution': 'Учебное заведение',
            'education_year': 'Год окончания',
            'previous_work_1': 'Предыдущее место работы 1',
            'previous_work_2': 'Предыдущее место работы 2',
            'previous_work_3': 'Предыдущее место работы 3',
            'hire_date': 'Дата приема',
            'dismissal_date': 'Дата увольнения',
            'is_active': 'Работает',
        }
