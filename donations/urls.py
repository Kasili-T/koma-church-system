from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.index, name='index'),  # Redirects /donations/ to finances dashboard
    path('finances/', views.finances_dashboard, name='finances'),
    path('list/', views.donation_list, name='summary'),
    path('<int:pk>/', views.donation_detail, name='detail'),
    
    # ---- Donation Routes ----
    path('donate/', views.add_donation, name='make_donation'),  # renamed for clarity
    path('contribute/', views.add_donation, name='make_contribution'),  # alias for dashboard link

    # ---- Expense Routes ----
    path('expense/add/', views.add_expense, name='add_expense'),
]
