from django.core.management.base import BaseCommand
from meta_app.workstations.models import Workstation, Department


class Command(BaseCommand):
    help = 'Миграция существующих участков в новую структуру подразделений'

    def handle(self, *args, **options):
        # 1. Создаём подразделения
        production, _ = Department.objects.get_or_create(
            code='PROD',
            defaults={'name': 'Производство', 'order': 1}
        )
        office, _ = Department.objects.get_or_create(
            code='OFFICE',
            defaults={'name': 'Офис', 'order': 2}
        )
        warehouse, _ = Department.objects.get_or_create(
            code='WAREHOUSE',
            defaults={'name': 'Склад', 'order': 3}
        )

        # 2. Создаём подразделения внутри Производства
        meta_cut, _ = Department.objects.get_or_create(
            code='META_CUT',
            defaults={'name': 'Мета резка', 'parent': production, 'order': 1}
        )
        meta_assembly, _ = Department.objects.get_or_create(
            code='META_ASSEMBLY',
            defaults={'name': 'Мета сборка', 'parent': production, 'order': 2}
        )
        meta_letter, _ = Department.objects.get_or_create(
            code='META_LETTER',
            defaults={'name': 'Мета Буква', 'parent': production, 'order': 3}
        )

        # 3. Связываем существующие участки с новыми подразделениями
        # Сопоставляем по названию или сокращению
        workstation_map = {
            'ЧПУ Фрезер': meta_cut,
            'ЧПУ Лазер': meta_cut,
            'Постобработка': meta_assembly,
            'МетаСборка': meta_assembly,
            'Склад': warehouse,
            'Офис': office,
        }

        updated_count = 0
        for ws_name, department in workstation_map.items():
            workstation = Workstation.objects.filter(name=ws_name).first()
            if workstation:
                workstation.department = department
                workstation.save()
                updated_count += 1
                self.stdout.write(f"✅ {ws_name} → {department.full_path}")
            else:
                self.stdout.write(f"⚠️ Участок '{ws_name}' не найден")

        self.stdout.write(self.style.SUCCESS(f'🎉 Обновлено участков: {updated_count}'))
