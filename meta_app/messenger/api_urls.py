# meta_app/messenger/api_urls.py
from django.urls import path
from . import views

app_name = 'messenger_api'

urlpatterns = [
    path('chats/', views.get_chats, name='get_chats'),
]
