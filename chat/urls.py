from django.urls import path
from . import views

app_name = 'chat'  # important for {% url 'chat:chat_rooms' %}

urlpatterns = [
    path('rooms/', views.chat_rooms_view, name='chat_rooms'),
    path('rooms/<str:room_name>/', views.chat_room, name='chat_room'),
]
