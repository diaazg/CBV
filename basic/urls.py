from django.urls import path, include
from .views import RegisterView,GetUsersView,LoginView,TokenValidationView




urlpatterns = [
    path('register', RegisterView.as_view(),name='register'),
    path('login', LoginView.as_view(),name='login'),
    path('getall', GetUsersView.as_view(),name='get_all'),
    path('checkToken',TokenValidationView.as_view())
    
]
