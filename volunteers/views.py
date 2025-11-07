from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Volunteer, VolunteerOpportunity

# -----------------------------
# Helper: Check if user is admin
# -----------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser


# =====================================================
# USER SIDE
# =====================================================
@login_required
def volunteer_dashboard(request):
    """User dashboard - view available opportunities & application status."""
    opportunities = VolunteerOpportunity.objects.all().order_by('department')
    applications = Volunteer.objects.filter(user=request.user).order_by('-applied_on')

    common_roles = {
        "Ushering / Hospitality": "Welcoming members, helping with seating, managing events.",
        "Choir / Music Ministry": "Singing, playing instruments, supporting worship services.",
        "Teaching / Sunday School": "Teaching children or youth.",
        "Media / Technical": "Managing sound, video, livestream, presentations.",
        "Prayer Ministry": "Interceding, counseling, or support.",
        "Outreach / Community Service": "Visiting hospitals, helping in charity work.",
        "Event Support": "Setting up events, serving refreshments, logistics."
    }

    return render(request, 'volunteers/dashboard.html', {
        'opportunities': opportunities,
        'applications': applications,
        'common_roles': common_roles
    })


@login_required
def apply_volunteer(request):
    """User applies for a volunteer opportunity."""
    opportunities = VolunteerOpportunity.objects.all().order_by('department')

    if request.method == "POST":
        opp_id = request.POST.get("opportunity")
        availability = request.POST.get("availability")

        opportunity = get_object_or_404(VolunteerOpportunity, id=opp_id)

        if Volunteer.objects.filter(
            user=request.user,
            opportunity=opportunity,
            status__in=['Pending', 'Approved']
        ).exists():
            messages.warning(request, f"You already applied for {opportunity.department}.")
            return redirect("volunteers:volunteer_dashboard")

        Volunteer.objects.create(
            user=request.user,
            opportunity=opportunity,
            availability=availability,
            status="Pending"
        )
        messages.success(request, f"Your volunteer application for {opportunity.department} was submitted.")
        return redirect("volunteers:volunteer_dashboard")

    return render(request, "volunteers/apply.html", {"opportunities": opportunities})


# =====================================================
# ADMIN SIDE - Manage Volunteer Applications
# =====================================================
@login_required
@user_passes_test(is_admin)
def admin_volunteer_list(request):
    """Admin view - list all volunteers with search."""
    query = request.GET.get('q', '')
    volunteers = Volunteer.objects.select_related('user', 'opportunity').order_by('-applied_on')

    if query:
        volunteers = volunteers.filter(
            user__username__icontains=query
        ) | volunteers.filter(opportunity__department__icontains=query)

    return render(request, 'volunteers/admin_volunteer_list.html', {'volunteers': volunteers, 'query': query})


@login_required
@user_passes_test(is_admin)
def update_volunteer_status(request, pk, status):
    """Approve or reject volunteers quickly from admin panel."""
    volunteer = get_object_or_404(Volunteer, pk=pk)
    volunteer.status = status
    volunteer.save()

    # Send email notification
    subject = f"Volunteer Application {status}"
    message = (
        f"Dear {volunteer.user.first_name or volunteer.user.username},\n\n"
        f"Your volunteer application for the {volunteer.opportunity.department} department "
        f"has been {status.lower()}.\n\n"
        f"Blessings,\nKOMA Church Administration"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [volunteer.user.email])

    messages.success(request, f"Volunteer {volunteer.user.username}'s status updated to {status}.")
    return redirect('volunteers:admin_volunteer_list')


# =====================================================
# ADMIN SIDE - Manage Volunteer Opportunities
# =====================================================
@login_required
@user_passes_test(is_admin)
def admin_opportunities(request):
    opportunities = VolunteerOpportunity.objects.all().order_by('department')
    return render(request, 'volunteers/admin_opportunities.html', {'opportunities': opportunities})


@login_required
@user_passes_test(is_admin)
def add_opportunity(request):
    if request.method == 'POST':
        department = request.POST['department']
        description = request.POST.get('description', '')
        availability = request.POST['required_availability']
        slots = request.POST.get('slots', 1)

        VolunteerOpportunity.objects.create(
            department=department,
            description=description,
            required_availability=availability,
            slots=slots
        )
        messages.success(request, f"Volunteer opportunity '{department}' added successfully.")
        return redirect('volunteers:admin_opportunities')

    return render(request, 'volunteers/add_opportunity.html')


@login_required
@user_passes_test(is_admin)
def edit_opportunity(request, id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=id)
    if request.method == 'POST':
        opportunity.department = request.POST['department']
        opportunity.description = request.POST.get('description', '')
        opportunity.required_availability = request.POST['required_availability']
        opportunity.slots = request.POST.get('slots', 1)
        opportunity.save()

        messages.success(request, f"Volunteer opportunity '{opportunity.department}' updated successfully.")
        return redirect('volunteers:admin_opportunities')

    return render(request, 'volunteers/edit_opportunity.html', {'opportunity': opportunity})


@login_required
@user_passes_test(is_admin)
def delete_opportunity(request, id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=id)
    opportunity.delete()
    messages.success(request, f"Volunteer opportunity '{opportunity.department}' deleted successfully.")
    return redirect('volunteers:admin_opportunities')
from django.shortcuts import render

def volunteer_portal(request):
    """Public volunteer portal for members"""
    return render(request, 'volunteers/volunteer_portal.html')
