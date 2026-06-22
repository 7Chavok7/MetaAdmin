from django import forms
from .models import DailyAttendance


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
