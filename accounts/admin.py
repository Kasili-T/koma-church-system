from django.contrib import admin
from .models import Member, Role, AttendanceRecord, Event, Volunteer
from .models import PrayerTeam, PrayerRequest, PrayerReaction

# Register simple models
admin.site.register(PrayerTeam)
admin.site.register(Member)
admin.site.register(Role)
admin.site.register(Event)
admin.site.register(Volunteer)
admin.site.register(AttendanceRecord)

# Register PrayerRequest with custom admin display
@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('title', 'description', 'user__username')

# Register PrayerReaction model
@admin.register(PrayerReaction)
class PrayerReactionAdmin(admin.ModelAdmin):
    list_display = ('prayer', 'user', 'created_at')
