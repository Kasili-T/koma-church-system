from django.db import models
from accounts.models import Member
from django.utils import timezone

class Donation(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'Mpesa'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    CATEGORY_CHOICES = [
        ('tithe', 'Tithe'),
        ('offering', 'Offering'),
        ('charity', 'Charity'),
        ('building', 'Building Fund'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    date_donated = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    def __str__(self):
        return f"{self.member.user.username} - {self.amount} ({self.payment_method})"

from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('charity', 'Charity'),
        ('event', 'Event'),
        ('salary', 'Salary'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date_recorded = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"
