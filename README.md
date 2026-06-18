# MetaAdmin

Система учета рабочего времени производства.

## Описание
Веб-приложение для учета сотрудников, квалификаций и рабочего времени на производственных участках.

## Технологии
- Python 3.12
- Django 5.0.1
- SQLite (разработка) / PostgreSQL (продакшн)
- Bootstrap 5

## Установка для разработки

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver