from django.core.management.base import BaseCommand
from meta_app.employees.models import Skill


class Command(BaseCommand):
    help = 'Создает начальные навыки'

    def handle(self, *args, **options):
        skills_data = [
            # Производство
            {'name': 'сборка', 'category': 'production'},
            {'name': 'сборка "Мета Буква"', 'category': 'production'},
            {'name': 'лазер', 'category': 'production'},
            {'name': 'лазерный гравер', 'category': 'production'},
            {'name': 'фрезер', 'category': 'production'},
            {'name': 'клише', 'category': 'production'},
            {'name': '3d обработка', 'category': 'production'},

            # Склад
            {'name': 'кладовщик', 'category': 'warehouse'},

            # Офис
            {'name': 'менеджер', 'category': 'office'},
            {'name': 'технолог', 'category': 'office'},
        ]

        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={'category': skill_data['category']}
            )
            if created:
                self.stdout.write(f"✅ Создан навык: {skill.name}")
            else:
                self.stdout.write(f"⏩ Навык уже существует: {skill.name}")

        self.stdout.write(self.style.SUCCESS('🎉 Все навыки созданы!'))
