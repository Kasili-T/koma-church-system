from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# =====================================================
# Role Model
# =====================================================
class Role(models.Model):
    """Defines roles for members (Admin, Pastor, Leader, Member, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


# =====================================================
# Member Model (User Profile)
# =====================================================
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        blank=True,
        null=True,
    )

    membership_status = models.CharField(
        max_length=20,
        choices=[("Active", "Active"), ("Inactive", "Inactive"), ("Pending", "Pending")],
        default="Active",
    )

    join_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    total_contributions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Members"

    def __str__(self):
        return self.user.username


# =====================================================
# Attendance Model
# =====================================================
class AttendanceRecord(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.now)
    event_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ("member", "date")
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.member.user.username} - {self.date}"


# =====================================================
# Volunteer Model
# =====================================================
class Volunteer(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="volunteer_roles")
    event = models.CharField(max_length=200)
    date = models.DateField()
    role = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "Volunteers"

    def __str__(self):
        return f"{self.member.user.username} - {self.event}"


# =====================================================
# Event Model
# =====================================================
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title


# =====================================================
# News / Announcements Model
# =====================================================
class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class PrayerTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class PrayerRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prayer_requests")
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # reactions is a many-to-many through PrayerReaction
    reactions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PrayerReaction',
        related_name='prayed_requests',
        blank=True
    )

    def __str__(self):
        return f"{self.title} — {self.user}"

    def reaction_count(self):
        return self.prayreactions.count()

    def reacted_by(self, user):
        return self.prayreactions.filter(user=user).exists()

    def visible_to(self, user):
        """Return True if `user` can see the request."""
        if not self.is_private:
            return True
        if not user.is_authenticated:
            return False
        # owners always see their own
        if self.user_id == getattr(user, 'id', None):
            return True
        # if you store role as user.role.name (string)
        role = getattr(user, 'role', None)
        if role and getattr(role, 'name', '').lower() in ('pastor', 'admin', 'leader'):
            return True
        # fallback: superusers
        if getattr(user, 'is_superuser', False):
            return True
        return False

class PrayerReaction(models.Model):
    prayer = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name="prayreactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prayer_reactions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("prayer", "user")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} prayed for {self.prayer_id}"




# =====================================================
# Notifications
# =====================================================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=150)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_sent"]

    def __str__(self):
        return f"{self.title} → {self.user.username}"


# =====================================================
# Signals: Auto Create Member Profile
# =====================================================
@receiver(post_save, sender=User)
def create_member_for_user(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)
from django.db import models
from django.contrib.auth.models import User

class MediaItem(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to="media-gallery/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
