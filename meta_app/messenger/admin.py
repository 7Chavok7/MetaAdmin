# /meta_app/messeger/admi.py | A.Grachev | 30.07.2026
from django.contrib import admin
from .models import Chat, ChatMessage, UserChatStatus


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_group',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        'is_group'
    ]
    filter_horizontal = [
        'participants'
    ]
    search_fields = [
        'name'
    ]
    

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'chat',
        'employee',
        'message',
        'created_at',
        'is_read'
    ]
    list_filter = [
        'is_read',
        'created_at'
    ]
    search_fields = [
        'message',
        'employee__short_name'
    ]
    
    
@admin.register(UserChatStatus)
class UserChatStatusAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'is_online',
        'last_seen'
    ]
    list_filter = [
        'is_online'
    ]