# meta_app/messenger/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        if not await self.is_participant():
            await self.close()
            return

        await self.set_user_online(True)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.set_user_online(False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'message':
                await self.handle_message(data)
            elif action == 'typing':
                await self.handle_typing(data)
        except Exception as e:
            print(f"Messenger error: {e}")

    async def handle_message(self, data):
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        message = await self.save_message(message_text)

        # ✅ Преобразуем время в локальное
        local_time = timezone.localtime(message.created_at)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'employee_id': self.user.id,
                'employee_full_name': self.user.full_name,
                'message': message.message,
                'created_at': local_time.strftime('%H:%M'),  # ← локальное время
            }
        )

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'employee_id': self.user.id,
                'employee_full_name': self.user.full_name,
                'is_typing': is_typing,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'employee_id': event['employee_id'],
            'employee_full_name': event['employee_full_name'],
            'message': event['message'],
            'created_at': event['created_at'],
        }))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'employee_id': event['employee_id'],
            'employee_full_name': event['employee_full_name'],
            'is_typing': event['is_typing'],
        }))

    async def online_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_status',
            'online_users': event['online_users'],
        }))

    @database_sync_to_async
    def is_participant(self):
        from django.contrib.auth import get_user_model
        from .models import Chat

        User = get_user_model()
        chat = Chat.objects.get(id=self.chat_id)
        return chat.participants.filter(id=self.user.id).exists()

    @database_sync_to_async
    def save_message(self, message_text):
        from django.contrib.auth import get_user_model
        from .models import Chat, ChatMessage

        User = get_user_model()
        chat = Chat.objects.get(id=self.chat_id)
        message = ChatMessage.objects.create(
            chat=chat,
            employee=self.user,
            message=message_text
        )
        chat.updated_at = timezone.now()
        chat.save()
        return message

    @database_sync_to_async
    def set_user_online(self, is_online):
        from .models import UserChatStatus

        status, created = UserChatStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.last_seen = timezone.now()
        status.save()

    @database_sync_to_async
    def get_online_users(self):
        from django.contrib.auth import get_user_model
        from .models import Chat

        User = get_user_model()
        chat = Chat.objects.get(id=self.chat_id)
        participants = chat.participants.all()
        online_users = []
        for user in participants:
            if hasattr(user, 'chat_status') and user.chat_status.is_online:
                online_users.append({
                    'id': user.id,
                    'full_name': user.full_name,
                })
        return online_users

    async def send_online_status(self):
        online_users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_status',
                'online_users': online_users,
            }
        )
