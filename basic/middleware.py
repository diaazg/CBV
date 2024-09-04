from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import UserInfo
from .services import update_last_connected_date


EXEMPT_PATHS = ['/admin/', '/basic/login', '/basic/register',
                '/basic/checkToken','/basic/invitation','/basic/friend']  

class JWTAuthenticationMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
       
        if any(request.path_info.startswith(path) for path in EXEMPT_PATHS):
            response = self.get_response(request)
            return response

        auth = JWTAuthentication()
        try:

            user, _ = auth.authenticate(request)

            if user is None:

                return JsonResponse({'error': 'Invalid or missing token'}, status=401)
            else:

               update_last_connected_date(user=user)                
               
        except (InvalidToken, TokenError) as e:
      
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        response = self.get_response(request)
        return response
