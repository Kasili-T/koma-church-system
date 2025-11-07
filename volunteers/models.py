# models.py
from django.db import models
from django.contrib.auth.models import User

# ------------------------------
# Admin-defined volunteer opportunities
# ------------------------------
class VolunteerOpportunity(models.Model):
    department = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    required_availability = models.CharField(max_length=100)
    slots = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.department


# ------------------------------
# User volunteer application
# ------------------------------
class Volunteer(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    availability = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'opportunity')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.user.username} - {self.opportunity.department}"


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Volunteer, VolunteerOpportunity

# ------------------------------
# Admin: List all volunteer applications
# ------------------------------
def admin_volunteer_list(request):
    volunteers = Volunteer.objects.select_related('user', 'opportunity').all()
    return render(request, 'volunteers/admin_volunteer_list.html', {'volunteers': volunteers})


# ------------------------------
# Admin: Approve a volunteer
# ------------------------------
def approve_volunteer(request, id):
    volunteer = get_object_or_404(Volunteer, id=id)
    volunteer.status = 'Approved'
    volunteer.save()
    return redirect('accounts:admin_volunteer_list')  # Use app namespace


# ------------------------------
# Admin: Reject a volunteer
# ------------------------------
def reject_volunteer(request, id):
    volunteer = get_object_or_404(Volunteer, id=id)
    volunteer.status = 'Rejected'
    volunteer.save()
    return redirect('accounts:admin_volunteer_list')  # Use app namespace
