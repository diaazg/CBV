from django import forms
from django.contrib.auth.models import User
from .models import *

class UserRegisterForm(forms.Form):
      
        username = forms.CharField(max_length=150,required=True)
        password = forms.CharField(min_length=5)
        email = forms.EmailField()
        phone_number = forms.CharField(max_length=12,min_length=12)
        profile_title = forms.CharField(max_length=120)

     
      


class UserLoginForm(forms.Form): ## use forms.Form if we don't want to check Model in db
        
         username = forms.CharField(max_length=150,required=True)
         password = forms.CharField(min_length=5)
     

         def clean_username(self):
           username = self.cleaned_data.get('username')
       
           if not User.objects.filter(username=username).exists():
             raise forms.ValidationError("Username does not exist.")
           return username


class InvitationForm(forms.ModelForm):

    class Meta:
        model =   Invitation
        fields = '__all__'  

class MessageForm(forms.ModelForm):
      
      class Meta:
        model =   Message
        fields = '__all__'  
               



        