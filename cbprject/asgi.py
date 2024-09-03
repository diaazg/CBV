# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import basic.routing  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cbprject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            basic.routing.websocket_urlpatterns  
        )
    ),
})
