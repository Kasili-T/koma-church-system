from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Donation, Expense
from .forms import DonationForm, ExpenseForm

# Redirect root /donations/ to finances dashboard
def index(request):
    return redirect('donations:finances')


# ---------------- Finances Dashboard ----------------
def finances_dashboard(request):
    donations_qs = Donation.objects.all()

    # Filter donations based on GET parameters
    start = request.GET.get('start')
    end = request.GET.get('end')
    method = request.GET.get('method')
    category = request.GET.get('category')

    if start:
        donations_qs = donations_qs.filter(date_donated__date__gte=start)
    if end:
        donations_qs = donations_qs.filter(date_donated__date__lte=end)
    if method:
        donations_qs = donations_qs.filter(payment_method=method)
    if category:
        donations_qs = donations_qs.filter(category=category)

    # Totals
    total_donations = donations_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_donations - total_expenses

    # Donations by category for chart
    categories = (
        Donation.objects
        .values('category')
        .annotate(total=Sum('amount'))
    )

    # Recent records
    recent_donations = donations_qs.order_by('-date_donated')[:12]
    recent_expenses = Expense.objects.order_by('-date_recorded')[:12]

    context = {
        'total_donations': total_donations,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'categories': categories,
        'donations': recent_donations,
        'expenses': recent_expenses,
    }

    return render(request, 'donations/finances.html', context)


# ---------------- Donations List & Detail ----------------
def donation_list(request):
    donations = Donation.objects.order_by('-date_donated')
    return render(request, 'donations/summary.html', {'donations': donations})


def donation_detail(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    return render(request, 'donations/donation_detail.html', {'donation': donation})


# ---------------- Add Donation ----------------
def add_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:dashboard')  # redirect user back to dashboard
    else:
        form = DonationForm()

    return render(request, 'donations/make_donation.html', {'form': form})


# ---------------- Add Expense ----------------
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donations:finances')
    else:
        form = ExpenseForm()

    return render(request, 'donations/expense_form.html', {'form': form})
