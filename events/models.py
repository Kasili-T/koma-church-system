from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # track updates

    class Meta:
        ordering = ['date']  # events are ordered by date
        verbose_name = "Event"
        verbose_name_plural = "Events"
        unique_together = ('title', 'date', 'location')  # prevents duplicates

    def __str__(self):
        return f"{self.title} on {self.date.strftime('%d %b %Y')}"

    def is_upcoming(self):
        """Return True if the event is upcoming."""
        return self.date >= timezone.localtime(timezone.now())


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'member')  # prevent duplicate registration
        ordering = ['-registered_at']
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"

    def __str__(self):
        return f"{self.member.username} registered for {self.event.title}"
