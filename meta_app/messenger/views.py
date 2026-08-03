from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Chat
from meta_app.employees.models import Employee


@login_required
def index(request):
    """Главная страница мессенджера"""
    return render(request, 'messenger/index.html', {
        'user': request.user,
    })


@login_required
def get_chats(request):
    """API для получения списка чатов пользователя"""
    chats = request.user.chats.all().order_by('-updated_at')

    data = []
    for chat in chats:
        data.append({
            'id': chat.id,
            # ← с именем собеседника
            'name': chat.get_display_name(request.user),
            'is_group': chat.is_group,
            'last_message': chat.last_message.message if chat.last_message else None,
            'updated_at': chat.updated_at.strftime('%H:%M'),
        })

    return JsonResponse({'chats': data})


@login_required
def get_messages(request, chat_id):
    """API для получения сообщений чата"""
    try:
        chat = Chat.objects.get(id=chat_id)

        if not chat.participants.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)

        messages_list = chat.messages.all().order_by('created_at')

        page = int(request.GET.get('page', 1))
        from django.core.paginator import Paginator
        paginator = Paginator(messages_list, 50)

        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)

        data = []
        for msg in page_obj:
            # ✅ Преобразуем UTC в локальное время (Europe/Moscow)
            local_time = timezone.localtime(msg.created_at)

            data.append({
                'id': msg.id,
                'employee_id': msg.employee.id,
                'employee_name': msg.employee.full_name,
                'message': msg.message,
                'created_at': local_time.strftime('%H:%M %d.%m.%Y'),
                'is_read': msg.is_read,
            })

        return JsonResponse({
            'messages': data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Чат не найден'}, status=404)


@login_required
def chat_create(request):
    """Создание нового чата"""
    if request.method == 'POST':
        participant_ids = request.POST.getlist('participants')
        is_group = request.POST.get('is_group') == 'on'
        chat_name = request.POST.get('chat_name', '').strip()

        if not participant_ids:
            messages.error(request, 'Выберите хотя бы одного участника')
            return redirect('/messenger/')

        participant_ids.append(str(request.user.id))
        participant_ids = list(set(participant_ids))

        # Проверяем, есть ли уже личный чат
        if not is_group and len(participant_ids) == 2:
            existing_chat = Chat.objects.filter(
                is_group=False,
                participants__id=participant_ids[0]
            ).filter(
                participants__id=participant_ids[1]
            ).first()

            if existing_chat:
                messages.info(
                    request, 'Чат с этим пользователем уже существует')
                return redirect('/messenger/')

        # Создаём чат
        chat = Chat.objects.create(
            name=chat_name if is_group else None,
            is_group=is_group,
            created_by=request.user,
        )
        chat.participants.set(participant_ids)

        messages.success(request, 'Чат создан!')
        return redirect('/messenger/')

    # GET запрос — показываем форму
    employees = Employee.objects.filter(
        is_active=True,
        is_superuser=False
    ).exclude(id=request.user.id).order_by('last_name', 'first_name')

    return render(request, 'messenger/create.html', {
        'employees': employees,
    })
