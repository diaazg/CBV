from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView,GetUsersView




urlpatterns = [
    path('register', RegisterView.as_view(),name='register'),
    path('getall', GetUsersView.as_view(),name='get_all'),
    
]
