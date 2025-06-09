from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_chat, name='api_chat'),
]
