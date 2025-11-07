from django.urls import path
from . import views

app_name = 'attendance'  # ✅ Important for namespacing in templates

urlpatterns = [
    # General Attendance Views
    path('', views.attendance_records, name='attendance_records'),
    path('mark/', views.mark_attendance, name='mark_attendance'),

    # User-Specific Attendance
    path('my/', views.my_attendance, name='my_attendance'),
    path('records/', views.records, name='records'),

    # Admin/Staff Attendance Management
    path('event/<int:event_id>/manage/', views.manage_event_attendance, name='manage_event_attendance'),
    path('event/<int:event_id>/save/', views.save_attendance, name='save_attendance'),  # ✅ Added to handle POST save
]
