from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Forum(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name


class Topic(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Post by {self.author.username} on {self.topic.title}"
