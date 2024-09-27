from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from .models import UserInfo
from .services import update_last_connected_date

EXEMPT_PATHS = ['/admin/', '/basic/login', '/basic/register',
                '/basic/checkToken', '/basic/invitation', '/basic/friend', '/ws/chat/', '/basic/message']

class JWTAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for WebSocket connections
        if request.headers.get('Upgrade') == 'websocket':
            return self.get_response(request)
        
        # Skip authentication for exempt paths
        if any(request.path_info.startswith(path) for path in EXEMPT_PATHS):
            return self.get_response(request)

        # Skip authentication for media and static file requests
        if request.path.startswith(settings.MEDIA_URL) or request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # Perform JWT authentication for all other requests
        auth = JWTAuthentication()
        try:
            user, _ = auth.authenticate(request)

            if user is None:
                return JsonResponse({'error': 'Invalid or missing token'}, status=401)
            else:
                update_last_connected_date(user=user)

        except (InvalidToken, TokenError):
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        return self.get_response(request)
