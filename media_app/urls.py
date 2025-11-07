from django.urls import path
from . import views

app_name = "media_app"

urlpatterns = [
    path('', views.media_list, name='media_list'),  # ✅ matches template
    path('<int:pk>/', views.media_detail, name='media_detail'),  # optional
]
