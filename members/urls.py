from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'roles', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
