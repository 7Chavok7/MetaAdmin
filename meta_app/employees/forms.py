from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """Форма для редактирования сотрудника"""

    class Meta:
        model = Employee
        fields = [
            'login',
            'employee_id',
            'card_number',
            'last_name',
            'first_name',
            'patronymic',
            'birth_date',
            'phone_number',
            'photo',
            'department',
            'base_salary',
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
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dismissal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'registration_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'residence_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'previous_work_1': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_2': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_3': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'education_specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'education_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'education_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'children_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'military_status': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'login': 'Логин для входа',
            'employee_id': 'Табельный номер',
            'card_number': 'Номер карточки',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'birth_date': 'Дата рождения',
            'phone_number': '№ телефона',
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
            'department': 'Подразделение',
            'is_active': 'Работает',
            'base_salary': 'Базовый оклад (руб.)',
        }


class EmployeeCreateForm(forms.ModelForm):
    """Форма для создания нового сотрудника"""

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте пароль'
        })
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = Employee
        fields = [
            'login',
            'employee_id',
            'card_number',
            'last_name',
            'first_name',
            'patronymic',
            'birth_date',
            'phone_number',
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
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dismissal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'registration_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'residence_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'previous_work_1': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_2': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_3': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'education_specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'education_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'education_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'children_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'military_status': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'login': 'Логин для входа',
            'employee_id': 'Табельный номер',
            'card_number': 'Номер карточки',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'birth_date': 'Дата рождения',
            'phone_number': '№ телефона',
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

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return password_confirm

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if Employee.objects.filter(login=login).exists():
            raise forms.ValidationError(
                'Пользователь с таким логином уже существует')
        return login

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError(
                'Сотрудник с таким табельным номером уже существует')
        return employee_id

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.set_password(self.cleaned_data['password'])
        if commit:
            employee.save()
        return employee


class EmployeeSelfEditForm(forms.ModelForm):
    """Форма для редактирования сотрудником своих данных (ограниченный набор полей)"""

    class Meta:
        model = Employee
        fields = [
            'patronymic',
            'birth_date',
            'phone_number',
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
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'registration_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'residence_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'previous_work_1': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_2': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_work_3': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'military_status': forms.Select(attrs={'class': 'form-control'}),
            'education_specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'education_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'education_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'children_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'has_children': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'patronymic': 'Отчество',
            'birth_date': 'Дата рождения',
            'phone_number': 'Телефон',
            'photo': 'Фото',
            'registration_address': 'Адрес регистрации',
            'residence_address': 'Адрес проживания',
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
        }
