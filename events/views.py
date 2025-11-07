from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Event, EventRegistration
import calendar

# ------------------------------
# Utility
# ------------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser

# ------------------------------
# General Events View (All Users)
# ------------------------------
@login_required
def events_view(request):
    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")
    selected_type = request.GET.get("type", "upcoming")

    now = timezone.now()
    events = Event.objects.all()

    # Filter by type
    if selected_type == "upcoming":
        events = events.filter(date__gte=now)
    elif selected_type == "past":
        events = events.filter(date__lt=now)

    # Filter by year/month
    if selected_year and selected_year.isdigit():
        events = events.filter(date__year=int(selected_year))
    if selected_month and selected_month.isdigit():
        events = events.filter(date__month=int(selected_month))

    events = events.order_by("date")

    # Dropdown options
    years = [y.year for y in Event.objects.dates("date", "year", order="DESC")]
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Registered events for the logged-in user
    registered_events = EventRegistration.objects.filter(member=request.user).values_list("event_id", flat=True)

    context = {
        "events": events,
        "years": years,
        "months": months,
        "selected_year": int(selected_year) if selected_year and selected_year.isdigit() else "",
        "selected_month": int(selected_month) if selected_month and selected_month.isdigit() else "",
        "selected_type": selected_type,
        "registered_events": registered_events,
    }

    return render(request, "events/events.html", context)

# ------------------------------
# Member Dashboard / Upcoming Events
# ------------------------------
@login_required
def member_events(request):
    current_time = timezone.localtime(timezone.now())

    # Upcoming events created by staff/admin
    events = Event.objects.filter(date__gte=current_time, created_by__is_staff=True).order_by('date')

    # Events already registered by the member
    registered_events = EventRegistration.objects.filter(member=request.user).values_list('event_id', flat=True)

    context = {
        'events': events,
        'registered_events': registered_events,
        'now': current_time,
    }
    return render(request, 'events/member_events.html', context)

# ------------------------------
# Event Registration
# ------------------------------
@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration, created = EventRegistration.objects.get_or_create(event=event, member=request.user)

    if created:
        messages.success(request, f"You have successfully registered for {event.title}.")
    else:
        messages.info(request, f"You are already registered for {event.title}.")

    return redirect("accounts:member_dashboard")  # Redirect to dashboard

# ------------------------------
# Admin Views: Registrations Overview
# ------------------------------
@login_required
@user_passes_test(is_admin)
def admin_view_registrations(request):
    events = Event.objects.prefetch_related("registrations__member").all()
    return render(request, "events/admin_registrations.html", {"events": events})

# ------------------------------
# Dashboard View (Upcoming Events for Members)
# ------------------------------
@login_required
def dashboard(request):
    current_time = timezone.localtime(timezone.now())
    events = Event.objects.filter(date__gte=current_time).order_by('date')
    registered_events = EventRegistration.objects.filter(member=request.user).values_list('event_id', flat=True)

    context = {
        'events': events,
        'registered_events': registered_events,
        'now': current_time,
    }
    return render(request, 'dashboard.html', context)
