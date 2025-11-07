from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    # ---------------- Member-Facing (Public/Volunteer) ----------------
    path('', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('portal/', views.volunteer_portal, name='volunteer_portal'),  # 👈 Added to fix NoReverseMatch
    path('apply/', views.apply_volunteer, name='apply_volunteer'),

    # ---------------- Admin-Facing ----------------
    path('admin/list/', views.admin_volunteer_list, name='admin_volunteer_list'),
    path('admin/update/<int:pk>/<str:status>/', views.update_volunteer_status, name='update_volunteer_status'),

    # ---- Volunteer Opportunities ----
    path('admin/opportunities/', views.admin_opportunities, name='admin_opportunities'),
    path('admin/opportunities/add/', views.add_opportunity, name='add_opportunity'),
    path('admin/opportunities/edit/<int:id>/', views.edit_opportunity, name='edit_opportunity'),
    path('admin/opportunities/delete/<int:id>/', views.delete_opportunity, name='delete_opportunity'),
]
