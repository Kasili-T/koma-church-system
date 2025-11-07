from django.db import models
from django.utils.timezone import now

class MediaItem(models.Model):
    MEDIA_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='photo')
    file = models.FileField(upload_to="media_uploads/", blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text="Optional external link (YouTube, etc.)")
    uploaded_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title
