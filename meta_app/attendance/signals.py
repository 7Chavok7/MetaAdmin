# meta_app/attendance/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DailyAttendance
from meta_app.employees.models import Employee, EmployeeSkill
from meta_app.workstations.models import EmployeeWorkstation


def send_update():
    """Отправить обновление всем клиентам через WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "updates",
            {
                "type": "update_message",
                "message": "Данные обновлены"
            }
        )
    except Exception as e:
        # Если WebSocket ещё не готов — просто игнорируем
        print(f"WebSocket не доступен: {e}")


# Сигналы для всех моделей, которые могут меняться
@receiver(post_save, sender=DailyAttendance)
@receiver(post_delete, sender=DailyAttendance)
@receiver(post_save, sender=Employee)
@receiver(post_delete, sender=Employee)
@receiver(post_save, sender=EmployeeSkill)
@receiver(post_delete, sender=EmployeeSkill)
@receiver(post_save, sender=EmployeeWorkstation)
@receiver(post_delete, sender=EmployeeWorkstation)
def data_changed(sender, **kwargs):
    send_update()