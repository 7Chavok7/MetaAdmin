import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from meta_app.attendance.routing import websocket_urlpatterns as attendance_ws
from meta_app.messenger.routing import websocket_urlpatterns as messenger_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

websocket_urlpatterns = attendance_ws + messenger_ws

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
