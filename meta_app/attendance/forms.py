# meta_app/attendace/forms.py | A.Grrachev
from django import forms
from .models import DailyAttendance, MonthlyWorkNorm, VacationRequest


class AttendanceForm(forms.ModelForm):
    """Форма для отметки прихода/ухода"""

    record_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = DailyAttendance
        fields = [
            'record_date',
            'workstation',
            'status',
            'is_weekend_shift',
            'start_time',
            'end_time',
            'overtime_hours',
            'note',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'workstation': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_weekend_shift': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'record_date': 'Дата',
            'workstation': 'Участок',
            'status': 'Статус',
            'is_weekend_shift': 'Работа в выходной',
            'start_time': 'Время начала',
            'end_time': 'Время окончания',
            'overtime_hours': 'Переработка (часов)',
            'note': 'Примечание',
        }


class MonthlyWorkNormBulkForm(forms.Form):
    """Форма для массового редактирования норм часов"""
    year = forms.IntegerField(
        label='Год',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Получаем год из kwargs
        year = kwargs.pop('year', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем начальное значение для года
        if year:
            self.initial['year'] = year

        months = [
            ('Январь', 1), ('Февраль', 2), ('Март', 3),
            ('Апрель', 4), ('Май', 5), ('Июнь', 6),
            ('Июль', 7), ('Август', 8), ('Сентябрь', 9),
            ('Октябрь', 10), ('Ноябрь', 11), ('Декабрь', 12),
        ]

        for month_name, month_num in months:
            field_name = f'month_{month_num}'
            self.fields[field_name] = forms.DecimalField(
                label=month_name,
                required=False,
                min_value=0,
                max_value=999,
                decimal_places=1,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': '—',
                    'style': 'width: 100px;'
                })
            )
            if year:
                try:
                    norm = MonthlyWorkNorm.objects.get(
                        year=year, month=month_num)
                    self.fields[field_name].initial = norm.hours_norm
                except MonthlyWorkNorm.DoesNotExist:
                    pass

        self.year = year


class MonthlyWorkNormForm(forms.ModelForm):
    """Форма для редактирования нормы часов"""

    class Meta:
        model = MonthlyWorkNorm
        fields = ['year', 'month', 'hours_norm']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-select'}, choices=[
                (1, 'Январь'), (2, 'Февраль'), (3, 'Март'),
                (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'),
                (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'),
                (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь'),
            ]),
            'hours_norm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
        labels = {
            'year': 'Год',
            'month': 'Месяц',
            'hours_norm': 'Норма часов',
        }


class VacationRequestForm(forms.ModelForm):
    """Форма для создания заявки на отпуск"""
    
    class Meta:
        model = VacationRequest
        fields = ['start_date', 'end_date', 'comment']
        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }),
            'end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }),
            'comment': forms.TextInput(
                attrs={
                    'rows': 2,
                    'class': 'form-control'
                }),
        }
        labels = {
            'start_date': 'Дата начала отпуска',
            'end_date': 'Даа окончания отпуска',
            'comment': 'Комментарий'
        }
        
    def clean(self):
        """Проверка на правильность ввода"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Дата начала не может быть позжк даты окончания')
        return cleaned_data
    
    
class VacationRequestProcessForm(forms.ModelForm):
    """Форма обработки заявки на отпуск (для начальника)"""
    
    class Meta:
        model = VacationRequest
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(
                attrs={
                    'class': 'form-select'
                }),
            'comment': forms.TextInput(
                attrs={
                    'rows': 2,
                    'class': 'form-control'
                })
        }
        labels = {
            'status': 'Статус',
            'comment': 'Комментарий'
        }