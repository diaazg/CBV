from django.views import View
from django.http import JsonResponse
from .forms import UserForm
from .services import create_user,get_all_users,generate_token
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
   
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserForm(data)
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


class GetUsersView(View):

      def get(self, request, *args, **kwargs):
          response = get_all_users()
          return JsonResponse({'users':response},status=200)      








