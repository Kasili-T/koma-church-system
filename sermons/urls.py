from django.urls import path
from . import views

app_name = "sermons"

urlpatterns = [
    path('', views.sermons_list, name='sermon_list'),
]
