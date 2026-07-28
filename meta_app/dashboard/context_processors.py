from meta_app.attendance.models import VacationRequest


def vacation_pending_count(request):
    """Количество заявок на отпуск, ожидающих подтверждения"""
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_manager):
        pending_count = VacationRequest.objects.filter(
            status='pending').count()
        return {'pending_vacations_count': pending_count}
    return {'pending_vacations_count': 0}
