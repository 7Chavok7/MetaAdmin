from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import DailyAttendance


@receiver(pre_save, sender=DailyAttendance)
def recalculate_hours_before_save(sender, instance, **kwargs):
    """Пересчет часов перед сохранением"""
    # Если изменился статус или время
    if instance.is_present and instance.start_time and instance.end_time:
        start = instance.start_time
        end = instance.end_time

        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute

        if end_minutes < start_minutes:
            end_minutes += 24 * 60

        diff_minutes = end_minutes - start_minutes

        # Вычитаем обед
        if diff_minutes > 6 * 60:
            diff_minutes -= 60

        hours = diff_minutes / 60
        instance.actual_hours = round(
            hours, 2) + float(instance.overtime_hours or 0)
    else:
        instance.actual_hours = 0
