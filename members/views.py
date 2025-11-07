from django.shortcuts import render
from rest_framework import viewsets, permissions
from accounts.models  import Member, Role
from .serializers import MemberSerializer, RoleSerializer


# --- DRF API Views ---
class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# --- Regular Django Views ---
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")
