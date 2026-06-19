from django.core.management.base import BaseCommand
from meta_app.workstations.models import Workstation


class Command(BaseCommand):
    help = 'Создает начальные участки'

    def handle(self, *args, **options):
        workstations_data = [
            {
                'name': 'ЧПУ Фрезер',
                'short_name': 'Фрез',
                'schedule_type': '5_2',
                'work_start': '08:00',
                'work_end': '17:00',
                'hours_per_day': 8,
                'color': '#007bff'
            },
            {
                'name': 'ЧПУ Лазер',
                'short_name': 'Лаз',
                'schedule_type': '5_2',
                'work_start': '08:00',
                'work_end': '17:00',
                'hours_per_day': 8,
                'color': '#28a745'
            },
            {
                'name': 'Постобработка',
                'short_name': 'Пост',
                'schedule_type': '5_2',
                'work_start': '08:00',
                'work_end': '17:00',
                'hours_per_day': 8,
                'color': '#17a2b8'
            },
            {
                'name': 'МетаСборка',
                'short_name': 'СбМ',
                'schedule_type': '5_2',
                'work_start': '08:00',
                'work_end': '17:00',
                'hours_per_day': 8,
                'color': '#ffc107'
            },
            {
                'name': 'Склад',
                'short_name': 'Склад',
                'schedule_type': '5_2',
                'work_start': '08:00',
                'work_end': '17:00',
                'hours_per_day': 8,
                'color': '#fd7e14'
            },
            {
                'name': 'Офис',
                'short_name': 'Офис',
                'schedule_type': '5_2',
                'work_start': '09:00',
                'work_end': '18:00',
                'hours_per_day': 8,
                'color': '#6f42c1'
            },
        ]

        for ws_data in workstations_data:
            workstation, created = Workstation.objects.get_or_create(
                name=ws_data['name'],
                defaults=ws_data
            )
            if created:
                self.stdout.write(f"✅ Создан участок: {workstation.name}")
            else:
                self.stdout.write(
                    f"⏩ Участок уже существует: {workstation.name}")

        self.stdout.write(self.style.SUCCESS('🎉 Все участки созданы!'))
