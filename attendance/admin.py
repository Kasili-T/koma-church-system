from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'event', 'status', 'date')
    list_filter = ('status', 'event')
    search_fields = ('member__username', 'event__title')
