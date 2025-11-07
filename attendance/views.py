from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Attendance
from events.models import Event
from calendar import month_name
from django.db.models import Count
from datetime import datetime
# ------------------------------
# Helper function
# ------------------------------
def is_admin(user):
    """Check if the user is staff or superuser."""
    return user.is_staff or user.is_superuser

# ------------------------------
# View: All Attendance Records (Admin)
# ------------------------------
@user_passes_test(is_admin)
def attendance_records(request):
    records = Attendance.objects.select_related('member', 'event').all()

    # Filtering
    event_filter = request.GET.get('event')
    if event_filter:
        records = records.filter(event__id=event_filter)

    events = Event.objects.all()
    members = User.objects.all()

    context = {
        'records': records,
        'events': events,
        'members': members,
    }
    return render(request, 'attendance/attendance_records.html', context)


# ------------------------------
# View: Mark Attendance Manually (Admin)
# ------------------------------
@user_passes_test(is_admin)
def mark_attendance(request):
    if request.method == 'POST':
        member_id = request.POST.get('member')
        event_id = request.POST.get('event')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')

        Attendance.objects.update_or_create(
            member_id=member_id,
            event_id=event_id,
            defaults={'status': status, 'remarks': remarks}
        )
        return redirect('attendance:attendance_records')

    events = Event.objects.all()
    members = User.objects.all()
    return render(request, 'attendance/mark_attendance.html', {'events': events, 'members': members})


# ------------------------------
# View: Logged-In User’s Own Attendance
# ------------------------------
@login_required


def my_attendance(request):
    records = Attendance.objects.filter(member=request.user)

    # Filters
    year = request.GET.get('year')
    month = request.GET.get('month')

    if year:
        records = records.filter(date__year=year)
    if month:
        records = records.filter(date__month=month)

    # Data for filters
    years = Attendance.objects.filter(member=request.user).dates('date', 'year')
    years = [y.year for y in years]
    months = {i: month_name[i] for i in range(1, 13)}

    # Chart data
    chart_data_qs = (
        records.values_list('date__month')
        .annotate(count=Count('id'))
        .order_by('date__month')
    )
    chart_labels = [month_name[m[0]] for m in chart_data_qs]
    chart_data = [m[1] for m in chart_data_qs]

    context = {
        'records': records,
        'years': years,
        'months': months,
        'total_attendances': records.count(),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'attendance/my_attendance.html', context)


# ------------------------------
# View: Manage Attendance per Event (Admin)
# ------------------------------
@user_passes_test(is_admin)
def manage_event_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    members = User.objects.all()

    if request.method == 'POST':
        for member in members:
            status = request.POST.get(f'status_{member.id}')
            if status:
                Attendance.objects.update_or_create(
                    member=member,
                    event=event,
                    defaults={'status': status}
                )
        return redirect('attendance:attendance_records')

    attendance_records = Attendance.objects.filter(event=event)
    return render(request, 'attendance/manage_event_attendance.html', {
        'event': event,
        'members': members,
        'attendance_records': attendance_records
    })


# ------------------------------
# View: Save Attendance via AJAX or POST (Optional)
# ------------------------------
@user_passes_test(is_admin)
def save_attendance(request, event_id):
    """Handles saving attendance updates (optional for AJAX forms)."""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('status_'):
                member_id = key.split('_')[1]
                Attendance.objects.update_or_create(
                    member_id=member_id,
                    event=event,
                    defaults={'status': value}
                )
        return redirect('attendance:manage_event_attendance', event_id=event.id)
    return redirect('attendance:attendance_records')
from django.shortcuts import render

def records(request):
    return render(request, 'attendance/records.html')
