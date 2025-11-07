# =====================================================
# Imports
# =====================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

# Models
from .models import Member, AttendanceRecord, Volunteer, Role, NewsPost, PrayerRequest
from donations.models import Donation  # ✅ Correct Donation model with 'member' field

# Forms
from .forms import DonationForm, PrayerRequestForm

# Serializers
from .serializers import MemberSerializer, RoleSerializer

# External services
from .mpesa import lipa_na_mpesa

# REST framework
from rest_framework import viewsets, permissions

# Standard libraries
import json
# Utility
# =====================================================
def is_admin(user):
    return user.is_staff or user.is_superuser


# =====================================================
# Authentication Views
# =====================================================
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# =====================================================
# Dashboards
# =====================================================
@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


# =====================================================
# Profile & Account Management
# =====================================================
@login_required
# accounts/views.py


def profile_view(request):
    # Ensure a Member profile exists for this user
    member, created = Member.objects.get_or_create(user=request.user)

    # Donations, Attendance, and Volunteering
    donations = Donation.objects.filter(member=member)
    attendance_records = AttendanceRecord.objects.filter(member=member)
    volunteer_roles = Volunteer.objects.filter(user=request.user)

    # Total donations
    total_donations = donations.aggregate(total=Sum("amount"))["total"] or 0

    # Chart Data (limit to latest 10 donations)
    ordered_donations = donations.order_by("date_donated")[:10]
    donation_chart_labels = [d.date_donated.strftime("%b %d") for d in ordered_donations]
    donation_chart_data = [float(d.amount) for d in ordered_donations]

    # Prepare context for the template
    context = {
        "user": request.user,
        "member": member,
        "profile_completion": 0,  # You can calculate this later
        "badges": [],
        "total_donations": total_donations,
        "events_attended_count": attendance_records.count(),
        "volunteer_count": volunteer_roles.count(),
        "recent_donations": donations.order_by("-date_donated")[:5],
        "attendance_history": attendance_records.order_by("-date")[:5],
        "volunteer_history": volunteer_roles.order_by("-applied_on")[:5],
        "recent_activity": [],  # Can later merge donations + attendance + volunteer logs

        # Charts
        "donation_chart_labels": donation_chart_labels,
        "donation_chart_data": donation_chart_data,
        "donation_mini_labels": donation_chart_labels[-5:],
        "donation_mini_data": donation_chart_data[-5:],

        # Attendance mini chart
        "attendance_mini_labels": [
            a.date.strftime("%b %d") for a in attendance_records.order_by("date")[:5]
        ],
        "attendance_mini_data": [1 for _ in attendance_records.order_by("date")[:5]],

        # Volunteer mini chart
        "volunteer_mini_labels": [
            v.applied_on.strftime("%b %d") for v in volunteer_roles.order_by("applied_on")[:5]
        ],
        "volunteer_mini_data": [1 for _ in volunteer_roles.order_by("applied_on")[:5]],
    }

    return render(request, "accounts/profile.html", context)

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def update_notifications(request):
    if request.method == "POST":
        messages.success(request, "Notification settings updated")
        return redirect("accounts:profile")
    return render(request, "accounts/update_notifications.html")


# =====================================================
# Donations & Contributions
# =====================================================
@login_required

@login_required
def donations_view(request):
    # Filter donations for the logged-in user's member profile
    donations = Donation.objects.filter(member__user=request.user).order_by("-date_donated")

    # Calculate total donations
    total_donations = donations.aggregate(total=Sum("amount"))["total"] or 0

    # Pass data to the template
    context = {
        "donations": donations,
        "total_donations": total_donations,
    }
    return render(request, "accounts/donations.html", context)


@login_required
def contributions(request):
    return render(request, "accounts/contributions.html")


@login_required
def make_donation(request):
    if request.method == "POST":
        form = DonationForm(request.POST)
        phone_number = request.POST.get("phone_number")
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user
            donation.save()

            # Trigger Mpesa STK Push
            response = lipa_na_mpesa(
                amount=donation.amount,
                phone_number=phone_number,
                account_reference=f"Donation-{donation.id}",
                transaction_desc="Church Donation",
            )

            if response.get("ResponseCode") == "0":
                return render(request, "accounts/donation_pending.html", {"donation": donation})
            else:
                donation.delete()
                form.add_error(None, "Mpesa payment failed. Try again.")
    else:
        form = DonationForm()
    return render(request, "accounts/make_donation.html", {"form": form})


@login_required
def make_contribution(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        purpose = request.POST.get("purpose")
        Donation.objects.create(
            member=request.user.member,
            amount=amount,
            method="Contribution",
        )
        messages.success(request, "Contribution successful!")
        return redirect("accounts:contributions")
    return render(request, "accounts/make_contribution.html")


# =====================================================
# Mpesa Callback
# =====================================================
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
    result_code = data["Body"]["stkCallback"]["ResultCode"]

    donation = Donation.objects.filter(id=checkout_request_id).first()
    if donation and result_code == 0:
        donation.paid = True
        donation.save()

    return HttpResponse("OK")


# =====================================================
# Attendance
# =====================================================
@login_required
def attendance_view(request):
    records = AttendanceRecord.objects.all()
    return render(request, "accounts/attendance.html", {"records": records})


# =====================================================
# Events, Chat, Forums
# =====================================================
# =====================================================
# User Event View (Member)
import calendar
@login_required
def events_view(request):
    from events.models import Event, EventRegistration  # import here to avoid circular import

    selected_year = request.GET.get("year")
    selected_month = request.GET.get("month")
    selected_type = request.GET.get("type", "upcoming")

    events = Event.objects.all()
    now = timezone.now()

    # --- Upcoming / Past filter ---
    if selected_type == "upcoming":
        events = events.filter(date__gte=now)
    elif selected_type == "past":
        events = events.filter(date__lt=now)

    # --- Year / Month filters ---
    if selected_year:
        events = events.filter(date__year=selected_year)
    if selected_month:
        events = events.filter(date__month=selected_month)

    # --- Sort events ---
    events = events.order_by("date")

    # --- Filter dropdowns ---
    years = [y.year for y in Event.objects.dates('date', 'year', order='DESC')]
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # --- Get registered events for logged-in user ---
    registered_events = []
    if request.user.is_authenticated:
        registered_events = EventRegistration.objects.filter(
            member=request.user
        ).values_list('event_id', flat=True)

    context = {
        "events": events,
        "years": years,
        "months": months,
        "selected_year": int(selected_year) if selected_year else "",
        "selected_month": int(selected_month) if selected_month else "",
        "selected_type": selected_type,
        "registered_events": registered_events,
    }

    return render(request, "events/events.html", context)

@login_required
def chat_view(request):
    return render(request, "accounts/chat.html")


@login_required
def forums_view(request):
    return render(request, "accounts/forums.html")


# =====================================================
# Member & Admin Management
# =====================================================
@login_required
@user_passes_test(is_admin)
def member_management(request):
    members = Member.objects.all()
    return render(request, "accounts/member_management.html", {"members": members})


@login_required
@user_passes_test(is_admin)
def event_management(request):
    return render(request, "accounts/event_management.html")


@login_required
@user_passes_test(is_admin)
def donations_finances(request):
    return render(request, "accounts/donations_finances.html")


@login_required
@user_passes_test(is_admin)
def reports_analytics(request):
    return render(request, "accounts/reports_analytics.html")


@login_required
@user_passes_test(is_admin)
def send_notifications(request):
    return render(request, "accounts/send_notifications.html")


# =====================================================
# News Feed / Volunteer / Prayer Requests
# =====================================================
@login_required
def news_feed(request):
    posts = NewsPost.objects.all().order_by("-created_at")
    return render(request, "accounts/news_feed.html", {"posts": posts})


@login_required
@user_passes_test(is_admin)
def create_news_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        NewsPost.objects.create(title=title, content=content, author=request.user)
        messages.success(request, "News post created successfully")
        return redirect("accounts:news_feed")
    return render(request, "accounts/create_news_post.html")


@login_required
@user_passes_test(is_admin)
def edit_news_post(request, post_id):
    post = get_object_or_404(NewsPost, id=post_id)
    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.save()
        messages.success(request, "News post updated")
        return redirect("accounts:news_feed")
    return render(request, "accounts/edit_news_post.html", {"post": post})


@login_required
@user_passes_test(is_admin)
def delete_news_post(request, post_id):
    post = get_object_or_404(NewsPost, id=post_id)
    post.delete()
    messages.success(request, "News post deleted")
    return redirect("accounts:news_feed")


@login_required
def volunteer_view(request):
    volunteers = Volunteer.objects.all()
    return render(request, "accounts/volunteer.html", {"volunteers": volunteers})


@login_required
def prayer_requests_view(request):
    requests = PrayerRequest.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.user = request.user
            prayer.save()
            messages.success(request, "Your prayer request has been submitted!")
            return redirect('accounts:prayer_requests')
    else:
        form = PrayerRequestForm()
    return render(request, 'accounts/prayer_requests.html', {'form': form, 'requests': requests})


@login_required
@user_passes_test(is_admin)
def manage_prayer_requests(request):
    requests = PrayerRequest.objects.all().order_by('-created_at')
    return render(request, 'accounts/manage_prayer_requests.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def news_feed_management(request):
    posts = NewsPost.objects.all()
    return render(request, "accounts/news_feed_management.html", {"posts": posts})


@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
# accounts/views.py


# Optional: only admin users can access
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def volunteer_management(request):
    # ------------------------------
    # Handle Approve/Reject actions
    # ------------------------------
    action = request.GET.get('action')
    volunteer_id = request.GET.get('id')
    
    if action in ['approve', 'reject'] and volunteer_id:
        volunteer = get_object_or_404(Volunteer, id=volunteer_id)
        if action == 'approve':
            volunteer.status = 'approved'
            messages.success(request, f"Volunteer {volunteer.user.get_full_name()} approved.")
        elif action == 'reject':
            volunteer.status = 'rejected'
            messages.warning(request, f"Volunteer {volunteer.user.get_full_name()} rejected.")
        volunteer.save()
        # Redirect to avoid resubmitting on refresh
        return redirect('accounts:volunteer_management')

    # ------------------------------
    # Filter & Search
    # ------------------------------
    volunteers = Volunteer.objects.all().select_related('user', 'opportunity')

    # Status filter
    status = request.GET.get('status')
    if status in ['pending', 'approved', 'rejected']:
        volunteers = volunteers.filter(status=status)

    # Search by name or department
    query = request.GET.get('q', '')
    if query:
        volunteers = volunteers.filter(
            user__first_name__icontains=query
        ) | volunteers.filter(
            user__last_name__icontains=query
        ) | volunteers.filter(
            opportunity__department__icontains=query
        )

    context = {
        'volunteers': volunteers.order_by('-applied_on'),
        'query': query,
    }

    return render(request, 'accounts/volunteer_management.html', context)

# =====================================================
# API ViewSets
# =====================================================
class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
from django.contrib.auth.models import User

# ------------------------------
# Edit Member
# ------------------------------
@login_required
@user_passes_test(is_admin)
def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    user = member.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        role_id = request.POST.get("role")

        # Update User
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update Role
        if role_id:
            role = Role.objects.get(id=role_id)
            member.role = role
            member.save()

        messages.success(request, "Member updated successfully!")
        return redirect("accounts:member_management")

    roles = Role.objects.all()
    context = {"member": member, "roles": roles}
    return render(request, "accounts/edit_member.html", context)


# ------------------------------
# Delete Member
# ------------------------------
@login_required
@user_passes_test(is_admin)
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        user = member.user
        member.delete()
        user.delete()  # Also delete associated user account
        messages.success(request, "Member deleted successfully!")
        return redirect("accounts:member_management")

    return render(request, "accounts/delete_member.html", {"member": member})
# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Event
from .forms import EventForm

# ------------------------------
# Utility
# ------------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser

# ------------------------------
# Member Dashboard
# ------------------------
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from events.models import Event

@login_required
def member_dashboard(request):
    # Show events from now onwards
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')

    context = {
        'events': events,
        'today': timezone.localtime(timezone.now()).date(),
    }
    return render(request, 'accounts/member_dashboard.html', context)

# Admin Event Management
# ------------------------------
@login_required
@user_passes_test(is_admin)
def event_management(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event saved successfully!")
            return redirect('accounts:event_management')
    else:
        form = EventForm()

    events = Event.objects.all().order_by('-date')
    total_events = events.count()
    upcoming_events = events.filter(date__gte=timezone.now().date()).count()

    return render(request, 'accounts/event_management.html', {
        'form': form,
        'events': events,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'today': timezone.now().date(),
    })

@login_required
@user_passes_test(is_admin)
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('accounts:event_management')
    else:
        form = EventForm()

    return render(request, 'accounts/event_form.html', {'form': form, 'title': 'Add Event'})

@login_required
@user_passes_test(is_admin)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('accounts:event_management')
    else:
        form = EventForm(instance=event)

    return render(request, 'accounts/event_form.html', {'form': form, 'title': 'Edit Event'})

@login_required
@user_passes_test(is_admin)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "Event deleted successfully!")
    return redirect('accounts:event_management')

# ------------------------------
# Event Reports (placeholder)
# ------------------------------
@login_required
def event_report(request):
    # Placeholder logic for future event reports
    return render(request, "accounts/event_report.html")
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Import models
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required

from donations.models import Donation
from events.models import Event
from volunteers.models import Volunteer
from accounts.models import Member
from attendance.models import Attendance  # optional

@login_required
def reports_analytics(request):
    current_year = timezone.now().year

    # -----------------------------
    # Total Counts
    # -----------------------------
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
from donations.models import Donation
from events.models import Event
from volunteers.models import Volunteer
from accounts.models import Member
from attendance.models import Attendance
from django.contrib.auth.decorators import login_required


@login_required
def reports_analytics(request):
    current_year = timezone.now().year

    # -----------------------------
    # Total Counts
    # -----------------------------
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_members = Member.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_events = Event.objects.count()

    # -----------------------------
    # Monthly Donations (Bar Chart)
    # -----------------------------
    monthly_data = (
        Donation.objects.filter(date_donated__year=current_year)
        .values_list('date_donated__month')
        .annotate(total=Sum('amount'))
        .order_by('date_donated__month')
    )
    donation_months = [datetime(2000, m, 1).strftime('%b') for m, _ in monthly_data]
    donation_totals = [total for _, total in monthly_data]

    # -----------------------------
    # Event Attendance (Line Chart)
    # -----------------------------
    try:
        attendance_data_qs = (
            Attendance.objects.filter(date__year=current_year)
            .values_list('date__month')
            .annotate(count=Count('id'))
            .order_by('date__month')
        )
        attendance_labels = [datetime(2000, m, 1).strftime('%b') for m, _ in attendance_data_qs]
        attendance_data = [count for _, count in attendance_data_qs]
    except Exception:
        attendance_labels = []
        attendance_data = []

    # -----------------------------
    # Volunteers by Department (Pie Chart)
    # -----------------------------
    volunteer_stats = (
        Volunteer.objects.values_list('opportunity__department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    volunteer_departments = [v[0] or "Unassigned" for v in volunteer_stats]
    volunteer_counts = [v[1] for v in volunteer_stats]

    # -----------------------------
    # Member Growth (Line Chart)
    # -----------------------------
    member_growth = (
        Member.objects.filter(join_date__year=current_year)
        .values_list('join_date__month')
        .annotate(count=Count('id'))
        .order_by('join_date__month')
    )
    member_growth_months = [datetime(2000, m, 1).strftime('%b') for m, _ in member_growth]
    member_growth_counts = [count for _, count in member_growth]

    # -----------------------------
    # Context
    # -----------------------------
    context = {
        "current_year": current_year,
        "total_donations": total_donations,
        "total_members": total_members,
        "total_volunteers": total_volunteers,
        "total_events": total_events,
        "donation_months": donation_months,
        "donation_totals": donation_totals,
        "attendance_labels": attendance_labels,
        "attendance_data": attendance_data,
        "volunteer_departments": volunteer_departments,
        "volunteer_counts": volunteer_counts,
        "member_growth_months": member_growth_months,
        "member_growth_counts": member_growth_counts,
    }

    return render(request, "accounts/reports_analytics.html", context)
# accounts/views.py
# accounts/views.py

from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from donations.models import Donation
from accounts.models import Member
from volunteers.models import Volunteer
from events.models import Event
from attendance.models import Attendance


def reports_pdf_view(request):
    """Generate dynamic Reports & Analytics (2025) PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    current_year = timezone.now().year

    # -------------------------------------------------------
    # HEADER
    # -------------------------------------------------------
    elements.append(Paragraph("<b>Reports &amp; Analytics (2025)</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # -------------------------------------------------------
    # SUMMARY METRICS
    # -------------------------------------------------------
    total_donations = Donation.objects.aggregate(total=Sum("amount"))["total"] or 0
    total_members = Member.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_events = Event.objects.count()

    summary_data = [
        ["💰 Total Donations", f"Ksh {total_donations:,}"],
        ["👥 Members", str(total_members)],
        ["🤝 Volunteers", str(total_volunteers)],
        ["📅 Events", str(total_events)],
    ]

    summary_table = Table(summary_data, colWidths=[250, 200])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # -------------------------------------------------------
    # MONTHLY DONATIONS
    # -------------------------------------------------------
    elements.append(Paragraph("<b>💰 Monthly Donations</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    monthly_donations = (
        Donation.objects.filter(date_donated__year=current_year)
        .annotate(month=TruncMonth("date_donated"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    if monthly_donations:
        donation_data = [["Month", "Total (Ksh)"]]
        for item in monthly_donations:
            donation_data.append([item["month"].strftime("%B"), f"{item['total']:,}"])
    else:
        donation_data = [["No donation data available"]]

    donation_table = Table(donation_data, colWidths=[250, 150])
    donation_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(donation_table)
    elements.append(Spacer(1, 20))

    # -------------------------------------------------------
    # EVENT ATTENDANCE
    # -------------------------------------------------------
    elements.append(Paragraph("<b>🧍 Event Attendance</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    attendance_data = (
        Attendance.objects.values("event__title")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    if attendance_data:
        attendance_table_data = [["Event", "Attendance Count"]]
        for record in attendance_data:
            attendance_table_data.append([record["event__title"], record["total"]])
    else:
        attendance_table_data = [["No attendance data available"]]

    attendance_table = Table(attendance_table_data, colWidths=[300, 100])
    attendance_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(attendance_table)
    elements.append(Spacer(1, 20))

    # -------------------------------------------------------
    # VOLUNTEERS BY OPPORTUNITY
    # -------------------------------------------------------
    elements.append(Paragraph("<b>🤝 Volunteers by Opportunity</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    volunteers_by_opportunity = (
        Volunteer.objects.values("opportunity__description")
        .annotate(total=Count("id"))
        .order_by("opportunity__description")
    )

    if volunteers_by_opportunity:
        volunteer_table_data = [["Opportunity Description", "Volunteers"]]
        for item in volunteers_by_opportunity:
            volunteer_table_data.append([item["opportunity__description"], item["total"]])
    else:
        volunteer_table_data = [["No volunteer data available"]]

    volunteer_table = Table(volunteer_table_data, colWidths=[300, 100])
    volunteer_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(volunteer_table)
    elements.append(Spacer(1, 20))

    # -------------------------------------------------------
    # MEMBER GROWTH
    # -------------------------------------------------------
    elements.append(Paragraph("<b>👥 Member Growth</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    member_growth = (
        Member.objects.filter(join_date__year=current_year)
        .annotate(month=TruncMonth("join_date"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    if member_growth:
        growth_table_data = [["Month", "New Members"]]
        for mg in member_growth:
            growth_table_data.append([mg["month"].strftime("%B"), mg["total"]])
    else:
        growth_table_data = [["No new members data available"]]

    growth_table = Table(growth_table_data, colWidths=[300, 100])
    growth_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(growth_table)
    elements.append(Spacer(1, 20))

    # -------------------------------------------------------
    # BUILD AND RETURN PDF
    # -------------------------------------------------------
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Reports_Analytics_2025.pdf"'
    return response
from django.shortcuts import render, redirect
from django.contrib import messages

# Placeholder for sending notifications
def send_notifications(request):
    if request.method == "POST":
        notification_message = request.POST.get("message")
        # TODO: Integrate with email/SMS push system
        messages.success(request, f"Notification sent: {notification_message}")
        return redirect('send_notifications')

    return render(request, "notifications/send_notifications.html")
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Member, Notification
 # if you have an in-app model

def admin_notifications(request):
    members = Member.objects.all()
    notifications = UserNotification.objects.order_by('-created_at')
    channel_layer = get_channel_layer()

    if request.method == "POST":
        message_text = request.POST.get("message")
        selected_members = request.POST.getlist("recipients")

        if message_text and selected_members:
            for member in Member.objects.filter(id__in=selected_members):
                notif = UserNotification.objects.create(user=member, message=message_text)
                async_to_sync(channel_layer.group_send)(
                    f"user_{member.id}",
                    {
                        "type": "send_notification",
                        "message": notif.message,
                    }
                )
            messages.success(request, "Real-time notification sent successfully!")
            return redirect('admin_notifications')
        else:
            messages.error(request, "Please enter a message and select recipients.")

    return render(request, "accounts/admin_dashboard_notifications.html", {
        "members": members,
        "notifications": notifications,
    })
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def member_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    # Optional: mark all as read when opened
    notifications.update(is_read=True)
    return render(request, "accounts/member_notifications.html", {"notifications": notifications})
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Notification

@login_required
def send_notifications(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        send_to = request.POST.get("send_to")

        if send_to == "all":
            users = User.objects.all()
        else:
            users = [request.user]  # customize later if you want filters

        for user in users:
            Notification.objects.create(user=user, title=title, message=message)

        messages.success(request, "✅ Notification sent successfully!")
        return redirect("accounts:send_notifications")

    return render(request, "accounts/send_notifications.html")
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Notification

def send_notifications(request):
    users = User.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        user_id = request.POST.get("user")

        if user_id:
            user = User.objects.get(id=user_id)
            Notification.objects.create(user=user, title=title, message=message)
        else:
            for user in users:
                Notification.objects.create(user=user, title=title, message=message)

        messages.success(request, "✅ Notification(s) sent successfully!")
        return redirect("accounts:send_notifications")

    return render(request, "accounts/send_notifications.html", {"users": users})
# accounts/views.py
# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification  # if you have a Notification model

@login_required
def my_notifications(request):
    """Display all notifications for the logged-in member."""
    notifications = []
    if hasattr(request.user, "member"):
        notifications = Notification.objects.filter(member=request.user.member).order_by("-date_sent")
    return render(request, "accounts/my_notifications.html", {"notifications": notifications})

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Notification
from events.models import Event

@login_required
def member_dashboard(request):
    # Get all notifications for this user
    notifications = Notification.objects.filter(user=request.user).order_by('-date_sent')

    # Get count of unread notifications
    unread_count = notifications.filter(is_read=False).count()

    # Get upcoming events (if needed)
    today = timezone.now().date()
    events = Event.objects.filter(date__gte=today).order_by('date')

    return render(request, 'accounts/member_dashboard.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'events': events,
        'today': today,
    })
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification  # make sure Notification model exists

@login_required
def mark_notifications_read(request):
    """Marks all unread notifications as read for the logged-in user."""
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "invalid request"}, status=400)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import AttendanceRecord  # or Attendance if that's your model name

@login_required
def my_attendance_view(request):
    """Show a logged-in user's attendance history."""
    attendance_records = AttendanceRecord.objects.filter(member__user=request.user)
    return render(request, "accounts/my_attendance.html", {"attendance_records": attendance_records})
# -------------------------------
# Sermons Management
# -------------------------------
@login_required
def sermons_view(request):
    return render(request, "accounts/sermons.html")

@login_required
def manage_sermons(request):
    return render(request, "accounts/manage_sermons.html")


# -------------------------------
# Media Gallery Management
# -------------------------------
@login_required
def media_gallery_view(request):
    return render(request, "accounts/media_gallery.html")

@login_required
def manage_media_gallery(request):
    return render(request, "accounts/manage_media_gallery.html")


# -------------------------------
# Prayer Requests Management
# -------------------------------
@login_required
def manage_prayer_requests(request):
    return render(request, "accounts/manage_prayer_requests.html")


# -------------------------------
# News Feed Management (Expanded)
# -------------------------------
@login_required
def manage_news_feed(request):
    return render(request, "accounts/manage_news_feed.html")
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PrayerRequest
from .forms import PrayerRequestForm

@login_required
def prayer_requests_view(request):
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.user = request.user
            prayer.save()
            messages.success(request, "Your prayer request has been submitted.")
            return redirect("accounts:prayer_requests")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PrayerRequestForm()

    requests = PrayerRequest.objects.filter(user=request.user).order_by("-created_at")
    
    return render(request, "accounts/prayer_requests.html", {
        "form": form,
        "requests": requests
    })
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from .models import PrayerRequest, PrayerReaction
from .forms import PrayerRequestForm

def user_is_pastor(user):
    role = getattr(user, 'role', None)
    return getattr(user, 'is_superuser', False) or (role and getattr(role, 'name', '').lower() in ('pastor', 'admin', 'leader'))
@login_required
def prayer_requests_view(request):
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.user = request.user
            prayer.save()

            if prayer.is_private:
                emails = getattr(settings, 'PRAYER_TEAM_EMAILS', [])
                if emails:
                    subject = f"[Prayer] New private request from {request.user.username}: {prayer.title}"
                    body = f"Title: {prayer.title}\n\nDescription:\n{prayer.description}\n\nSubmitted by: {request.user.get_full_name() or request.user.username}"
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=True)

            messages.success(request, "Your prayer request has been submitted.")
            return redirect("accounts:prayer_requests")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PrayerRequestForm()

    all_requests = PrayerRequest.objects.order_by("-created_at")
    visible_requests = [p for p in all_requests if p.visible_to(request.user)]

    return render(request, "accounts/prayer_requests.html", {
        "form": form,
        "prayer_requests": visible_requests,
    })


@login_required
def prayer_edit(request, pk):
    prayer = get_object_or_404(PrayerRequest, pk=pk)
    if prayer.user != request.user and not user_is_pastor(request.user):
        return HttpResponseForbidden("You don't have permission to edit this request.")
    if request.method == "POST":
        form = PrayerRequestForm(request.POST, instance=prayer)
        if form.is_valid():
            form.save()
            messages.success(request, "Prayer request updated.")
            return redirect("accounts:prayer_requests")
    else:
        form = PrayerRequestForm(instance=prayer)
    return render(request, "accounts/prayer_edit.html", {"form": form, "prayer": prayer})

@login_required
def prayer_delete(request, pk):
    prayer = get_object_or_404(PrayerRequest, pk=pk)
    if prayer.user != request.user and not user_is_pastor(request.user):
        return HttpResponseForbidden("You don't have permission to delete this request.")
    if request.method == "POST":
        prayer.delete()
        messages.success(request, "Prayer request deleted.")
        return redirect("accounts:prayer_requests")
    return render(request, "accounts/prayer_confirm_delete.html", {"prayer": prayer})

@login_required
def prayer_toggle_reaction(request, pk):
    """Toggle 'I prayed' reaction. Accept POST only."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    prayer = get_object_or_404(PrayerRequest, pk=pk)
    # check visibility (optional) — require visible to user
    if not prayer.visible_to(request.user):
        return JsonResponse({"error": "Not allowed"}, status=403)

    # Toggle
    existing = PrayerReaction.objects.filter(prayer=prayer, user=request.user)
    if existing.exists():
        existing.delete()
        reacted = False
    else:
        PrayerReaction.objects.create(prayer=prayer, user=request.user)
        reacted = True

    count = prayer.reaction_count()
    return JsonResponse({"reacted": reacted, "count": count})


# ---------------------------------
# Admin View – Manage All Requests
# ---------------------------------
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_prayer_requests(request):
    if request.method == "POST":
        req_id = request.POST.get("req_id")
        action = request.POST.get("action")

        prayer_request = get_object_or_404(PrayerRequest, id=req_id)

        if action == "assign":
            team = request.POST.get("team_assigned")
            prayer_request.team_assigned = team
            prayer_request.status = "Assigned"
            prayer_request.save()
            messages.success(request, f"Prayer request '{prayer_request.title}' assigned to {team}.")
        elif action == "answered":
            prayer_request.status = "Answered"
            prayer_request.save()
            messages.success(request, f"Prayer request '{prayer_request.title}' marked as answered.")

        return redirect("accounts:manage_prayer_requests")

    all_requests = PrayerRequest.objects.all().order_by("-created_at")
    return render(request, "accounts/manage_prayer_requests.html", {"all_requests": all_requests})
from .forms import NewsPostForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsPostForm

@login_required
def create_news_post(request):
    if not request.user.member.role or request.user.member.role.name != "Leader":
        messages.error(request, "Only Leaders are allowed to post announcements.")
        return redirect("accounts:news_feed")

    if request.method == "POST":
        form = NewsPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(request, "Announcement posted successfully!")
            return redirect("accounts:news_feed")
    else:
        form = NewsPostForm()

    return render(request, "accounts/news_feed_create.html", {"form": form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import PrayerRequest

@staff_member_required
def admin_prayer_requests(request):
    # Fetch all prayer requests
    prayer_requests = PrayerRequest.objects.select_related("user").all()
    return render(request, "accounts/admin_prayer_requests.html", {
        "prayer_requests": prayer_requests,
    })


@staff_member_required
def update_prayer_request(request, pk):
    prayer_request = get_object_or_404(PrayerRequest, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        team = request.POST.get("team_assigned")

        prayer_request.status = new_status
        prayer_request.team_assigned = team
        prayer_request.save()

        messages.success(request, f"Prayer request '{prayer_request.title}' updated successfully.")
        return redirect("accounts:admin_prayer_requests")

    return render(request, "accounts/update_prayer_request.html", {"prayer_request": prayer_request})


from django.shortcuts import redirect
from .models import PrayerRequest

def submit_prayer_request(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        PrayerRequest.objects.create(user=request.user, title=title, message=message)
        return redirect('accounts:dashboard')  # Redirect after submit
    return render(request, 'accounts/submit_prayer_request.html')
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import PrayerRequest, PrayerTeam

def update_prayer_request(request, pk):
    # Get the prayer request object or 404
    prayer_request = get_object_or_404(PrayerRequest, pk=pk)
    
    # Get all existing teams for the dropdown
    prayer_teams = PrayerTeam.objects.all()

    if request.method == "POST":
        # Get POSTed data
        team_input = request.POST.get("team_assigned")
        status = request.POST.get("status")

        # Assign the team properly
        prayer_request.team_assigned = None  # default

        if team_input:
            try:
                # Try to interpret as ID first
                prayer_request.team_assigned = PrayerTeam.objects.get(id=int(team_input))
            except (ValueError, PrayerTeam.DoesNotExist):
                # If it fails, try to find by name (fallback)
                try:
                    prayer_request.team_assigned = PrayerTeam.objects.get(name=team_input)
                except PrayerTeam.DoesNotExist:
                    prayer_request.team_assigned = None

        # Update status safely
        valid_status_choices = dict(PrayerRequest._meta.get_field('status').choices)
        if status in valid_status_choices:
            prayer_request.status = status

        # Save changes
        prayer_request.save()

        # Redirect back to admin prayer requests page
        return redirect("accounts:admin_prayer_requests")

    # GET request → render form
    return render(
        request,
        "accounts/admin_update_prayer_request.html",
        {
            "prayer_request": prayer_request,
            "prayer_teams": prayer_teams
        }
    )
from django.shortcuts import render, redirect, get_object_or_404
from sermons.models import Sermon

def sermons_view(request):
    sermons = Sermon.objects.all().order_by('-created_at')
    return render(request, "accounts/sermons.html", {"sermons": sermons})
def add_sermon(request):
    if request.method == "POST":
        title = request.POST.get("title")
        preacher = request.POST.get("preacher")
        media_url = request.POST.get("media_url")
        description = request.POST.get("description")
        Sermon.objects.create(
            title=title, preacher=preacher, media_url=media_url, description=description
        )
        return redirect("accounts:sermons")
    return render(request, "accounts/sermon_form.html")


def edit_sermon(request, id):
    sermon = get_object_or_404(Sermon, id=id)
    if request.method == "POST":
        sermon.title = request.POST.get("title")
        sermon.preacher = request.POST.get("preacher")
        sermon.media_url = request.POST.get("media_url")
        sermon.description = request.POST.get("description")
        sermon.save()
        return redirect("accounts:sermons")
    return render(request, "accounts/sermon_form.html", {"sermon": sermon})


def delete_sermon(request, id):
    sermon = get_object_or_404(Sermon, id=id)
    sermon.delete()
    return redirect("accounts:sermons")
from django import forms
from .models import MediaItem

class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['title', 'description', 'media_type', 'file']
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MediaItem
from .forms import MediaItemForm

@login_required
def media_gallery_create(request):
    if request.method == "POST":
        form = MediaItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            item.save()
            return redirect("accounts:media_gallery_list")
    else:
        form = MediaItemForm()
    return render(request, "accounts/media_gallery_form.html", {"form": form, "title": "Upload Media"})

@login_required
def media_gallery_edit(request, id):
    item = get_object_or_404(MediaItem, id=id)
    if request.method == "POST":
        form = MediaItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("accounts:media_gallery_list")
    else:
        form = MediaItemForm(instance=item)
    return render(request, "accounts/media_gallery_form.html", {"form": form, "title": "Edit Media"})

@login_required
def media_gallery_delete(request, id):
    item = get_object_or_404(MediaItem, id=id)
    item.delete()
    return redirect("accounts:media_gallery_list")
@login_required
def media_gallery_list(request):
    items = MediaItem.objects.all().order_by("-uploaded_at")
    return render(request, "accounts/media_gallery.html", {"items": items})
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsPost
from .forms import NewsPostForm

# Check if the user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

# ----------------------------
# Admin News Feed: list posts
# ----------------------------
@user_passes_test(is_admin)
def admin_news_feed(request):
    news_posts = NewsPost.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_news_feed.html', {'news_posts': news_posts})

# ----------------------------
# Admin Create News Post
# ----------------------------
@user_passes_test(is_admin)
def admin_create_news_post(request):
    if request.method == 'POST':
        form = NewsPostForm(request.POST)
        if form.is_valid():
            news_post = form.save(commit=False)
            news_post.author = request.user  # set author automatically
            news_post.save()
            messages.success(request, "News post created successfully!")
            return redirect('accounts:admin_news_feed')
    else:
        form = NewsPostForm()

    return render(request, 'accounts/admin_create_news_post.html', {'form': form})
from events.models import Event
from django.utils import timezone

def user_dashboard(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    return render(request, 'accounts/user_dashboard.html', {
        'upcoming_events': upcoming_events
    })
