from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.forum_list, name="forum_list"),  # ✅ fixed name
    path("<int:forum_id>/", views.topic_list, name="topic_list"),
    path("topic/<int:topic_id>/", views.topic_detail, name="topic_detail"),
]
