from django.views import View
from django.http import JsonResponse
from .forms import UserForm
from .services import create_user,get_all_users
import json



class RegisterView(View):
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserForm(data)
        if form.is_valid():
            try:
                create_user(form.cleaned_data)
                return JsonResponse({'message':'User added sucessfully'})
            except Exception as e:
                return JsonResponse({'errors': 'An error occurred'}, status=500)
            
        return JsonResponse({'errors': form.errors}, status=400)


class GetUsersView(View):

      def get(self, request, *args, **kwargs):
          response = get_all_users()
          return JsonResponse({'users':response},status=200)      








