from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    donor_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    phone_number = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '2547XXXXXXXX'
        })
    )

    class Meta:
        model = Donation
        fields = [
            'member',            # ✅ linked to registered member
            'category',
            'amount',
            'payment_method',
            'transaction_id',
            'status',
        ]
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not phone.startswith('2547') or len(phone) != 12 or not phone.isdigit():
            raise forms.ValidationError("Enter a valid Kenyan phone number (2547XXXXXXXX).")
        return phone

from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'category', 'added_by']
