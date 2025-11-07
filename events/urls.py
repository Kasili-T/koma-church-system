from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # ------------------------------
    # Public / Member-Facing Events
    # ------------------------------
    path('', views.events_view, name='events'),  # Shows upcoming/past events with filters

    # ------------------------------
    # Member-Specific Routes
    # ------------------------------
    path('member/events/', views.member_events, name='member_events'),  # Member dashboard view
    path('member/events/register/<int:event_id>/', views.register_event, name='register_event'),  # Register for an event

    # ------------------------------
    # Admin Routes
    # ------------------------------
    path('admin/events/registrations/', views.admin_view_registrations, name='admin_view_registrations'),  # Admin sees all registrations
]
