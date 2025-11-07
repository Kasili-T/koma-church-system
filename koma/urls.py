from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Welcome to Amazing Grace Chapel Management System 🎉")

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),

    # Accounts
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("accounts/", include("django.contrib.auth.urls")),

    # Apps
    path("chat/", include("chat.urls")),
    path("forum/", include("forum.urls")),
    path("sermons/", include(("sermons.urls", "sermons"), namespace="sermons")),
    path("media/", include("media_app.urls")),
    path("events/", include("events.urls")),
    path("donations/", include("donations.urls")),
    path("volunteers/", include("volunteers.urls")),
    path("attendance/", include("attendance.urls")),
    path("prayers/", include("prayers.urls")),
]

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
