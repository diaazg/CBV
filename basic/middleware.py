from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.urls import resolve

EXEMPT_URLS = ['login', 'register']  

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Middleware triggered for path: {request.path_info}")
        
        current_url = resolve(request.path_info).url_name
        print(f"Resolved URL name: {current_url}")

       
        if current_url not in EXEMPT_URLS:
            print("Checking for JWT token...")
            auth = JWTAuthentication()
            try:
               
                user_auth_tuple = auth.authenticate(request)
                if user_auth_tuple is None:
                    
                    
                    return JsonResponse({'error': 'Invalid or missing token'}, status=401)
                 
                
            except (InvalidToken, TokenError):
                
                return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        response = self.get_response(request)
        return response