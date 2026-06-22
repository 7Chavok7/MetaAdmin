from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meta_app.attendance'

    def ready(self):
        import meta_app.attendance.signals  # noqa
