from django.views import View
from django.http import JsonResponse
from .forms import UserRegisterForm,UserLoginForm
from .services import create_user,get_all_users,generate_token,verify_user
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
   
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserRegisterForm(data)
        if form.is_valid():
            try:
                user  =   create_user(form.cleaned_data)
                token = generate_token(user)
                token_obj = {
                    'refresh':str(token),
                    'access':str(token.access_token)
                }

                return JsonResponse({'message':token_obj})
            except Exception as e:
                return JsonResponse({'errors': 'An error occurred'}, status=500)
            
        return JsonResponse({'errors': form.errors}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserLoginForm(data)

        if form.is_valid():
            username = data['username']
            password = data['password']
            user = verify_user(username=username,password=password)
            if user:
                token = generate_token(user)
                token_obj = {
                    'refresh':str(token),
                    'access':str(token.access_token)
                }

                return JsonResponse({'message':token_obj})
            else:
                return JsonResponse({'error': 'Wrong credentials'}, status=404)
        else:
            return JsonResponse({'errors': form.errors}, status=400)    


class GetUsersView(View):

      def get(self, request, *args, **kwargs):
          response = get_all_users()
          return JsonResponse({'users':response},status=200)      








