from django.contrib import admin
from .models import Donation, Expense

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'amount', 'payment_method', 'category', 'status', 'date_donated')
    list_filter = ('payment_method', 'category', 'status')
    search_fields = ('member__user__username', 'transaction_id')

    # ✅ Add this method to display the member’s username or full name
    def member_name(self, obj):
        return obj.member.user.get_full_name() or obj.member.user.username
    member_name.short_description = 'Donor Name'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'date_recorded', 'added_by')
    list_filter = ('category',)
    search_fields = ('title', 'description')
