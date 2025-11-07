from django.urls import path
from . import views

app_name = 'prayers'

urlpatterns = [
    path('requests/', views.prayer_requests, name='requests'),
]
