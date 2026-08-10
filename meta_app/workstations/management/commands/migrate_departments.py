from django.core.management.base import BaseCommand
from meta_app.workstations.models import Department


class Command(BaseCommand):
    help = 'Создать структуру подразделений (без привязки участков)'

    def handle(self, *args, **options):
        self.stdout.write("🏗️ Создаю структуру подразделений...")

        # 1. Подразделения верхнего уровня
        production, created = Department.objects.get_or_create(
            code='PROD',
            defaults={
                'name': 'Производство',
                'description': 'Основное производство',
                'order': 1,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {production.name} (code: {production.code})")

        office, created = Department.objects.get_or_create(
            code='OFFICE',
            defaults={
                'name': 'Офис',
                'description': 'Административный отдел',
                'order': 2,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {office.name} (code: {office.code})")

        warehouse, created = Department.objects.get_or_create(
            code='WAREHOUSE',
            defaults={
                'name': 'Склад',
                'description': 'Складские помещения',
                'order': 3,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {warehouse.name} (code: {warehouse.code})")

        # 2. Подразделения внутри Производства
        meta_cut, created = Department.objects.get_or_create(
            code='META_CUT',
            defaults={
                'name': 'Мета резка',
                'parent': production,
                'description': 'Участки лазерной и фрезерной резки',
                'order': 1,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {meta_cut.name} → {meta_cut.parent.name}")

        meta_assembly, created = Department.objects.get_or_create(
            code='META_ASSEMBLY',
            defaults={
                'name': 'Мета сборка',
                'parent': production,
                'description': 'Сборочные участки',
                'order': 2,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {meta_assembly.name} → {meta_assembly.parent.name}")

        meta_letter, created = Department.objects.get_or_create(
            code='META_LETTER',
            defaults={
                'name': 'Мета Буква',
                'parent': production,
                'description': 'Участки производства букв',
                'order': 3,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {meta_letter.name} → {meta_letter.parent.name}")

        # 3. Подразделения внутри Мета резка
        cutting, created = Department.objects.get_or_create(
            code='CUTTING',
            defaults={
                'name': 'Резка',
                'parent': meta_cut,
                'description': 'Участки резки металла',
                'order': 1,
                'is_active': True
            }
        )
        self.stdout.write(f"   {'🆕' if created else '✅'} {cutting.name} → {cutting.parent.name}")

        # 4. Вывод итогов
        self.stdout.write("")
        self.stdout.write("📊 Итоговая структура:")
        self.stdout.write("")
        
        for dept in Department.objects.filter(parent__isnull=True, is_active=True).order_by('order'):
            self.stdout.write(f"📁 {dept.name} ({dept.code})")
            for child in dept.children.filter(is_active=True).order_by('order'):
                self.stdout.write(f"   ├── 📂 {child.name} ({child.code})")
                for grandchild in child.children.filter(is_active=True).order_by('order'):
                    self.stdout.write(f"   │   └── 📂 {grandchild.name} ({grandchild.code})")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f'🎉 Готово! Создано подразделений: {Department.objects.count()}'
        ))
        self.stdout.write("")
        self.stdout.write("📌 Теперь в админке можно привязать участки к подразделениям:")
        self.stdout.write("   → Зайдите в /admin/workstations/workstation/")
        self.stdout.write("   → Выберите участок → укажите поле 'Подразделение'")