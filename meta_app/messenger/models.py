# /meta_app/messenger/models.py | A.Grachev | 30.07.2026
from django.db import models
from django.utils import timezone


class Chat(models.Model):
    """Чат (личный или группы)"""

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Название чата'
    )
    participants = models.ManyToManyField(
        'employees.Employee',
        related_name='chats',
        verbose_name='Участники'
    )
    is_group = models.BooleanField(
        default=False,
        verbose_name='Групповой чат'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    created_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_chats',
        verbose_name='Создал'
    )

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group:
            return self.name or f"Групповой чат #{self.id}"
        else:
            participants = self.participants.all()
            if participants.count() == 2:
                return " - ".join([p.short_name for p in participants])
            return f"Личный чат #{self.id}"

    def get_display_name(self, user):
        """Получить отображаемое имя чата для конкретного пользователя"""
        if self.is_group:
            return self.name or "Групповой чат"
        else:
            participants = self.participants.all()
            if participants.count() == 2:
                # Находим собеседника
                other = participants.exclude(id=user.id).first()
                if other:
                    return other.full_name  # или other.short_name для сокращенного
            return "Личный чат"

    @property
    def display_name(self):
        """Отображаемое имя (без пользователя) — для админки"""
        if self.is_group:
            return self.name or "Групповой чат"
        else:
            participants = self.participants.all()
            if participants.count() == 2:
                return " - ".join([p.short_name for p in participants])
            return f"Личный чат #{self.id}"

    @property
    def last_message(self):
        return self.messages.first()

    @property
    def unread_count(self):
        return 0
    

class ChatMessage(models.Model):
    """Сообщения в чате"""
    
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат'
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Автор'
    )
    message = models.TextField(
        verbose_name='Сообщение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата и время прочтения'
    )
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.employee.short_name} - {self.message[:20]}"
    
    def mark_as_read(self):
        """Отметка о прочтении"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
            

class UserChatStatus(models.Model):
    """Статус пользователя в чате (online/offline)"""
    
    user = models.OneToOneField(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='chat_status',
        verbose_name='Пользователь'
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name='Онлайн'
    )
    last_seen = models.DateTimeField(
        default=timezone.now,
        verbose_name="Последний раз"
    )
    
    class Meta:
        verbose_name = 'Статус пользователя'
        verbose_name_plural = 'Статусы пользователей'
        
    def __str__(self):
        status = "онлайн" if self.is_online else "офлайн"
        return f"{self.user.short_name}: {status}"
    