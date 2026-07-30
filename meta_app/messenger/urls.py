# /meta_app/messenger/urls.py | A.Grachev | 30.07.2026
from django.urls import path
from . import views


app_name = 'messenger'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.chat_create, name='chat_create'),
    path('api/chats/', views.get_chats, name='get_chats'),
    path('api/messages/<int:chat_id>/', views.get_messages, name='get_messages'),
]
