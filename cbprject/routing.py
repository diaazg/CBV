# cbprject/routing.py
from basic import consumers  # Adjust based on where consumers.py is located
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.DirectChatConsumer.as_asgi()),
]
