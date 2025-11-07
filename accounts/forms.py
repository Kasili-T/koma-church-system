from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from donations.models import Donation
from .models import NewsPost, PrayerRequest, Event, MediaItem


# ===========================
# User Signup Form
# ===========================
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# ===========================
# Donation Form
# ===========================
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['member', 'amount', 'payment_method', 'category', 'status']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter amount', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# ===========================
# News Post Form
# ===========================
class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ['title', 'content']  # make sure 'is_published' is not here
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter news title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter news content', 'rows': 3}),
        }


# ===========================
# Prayer Request Form
# ===========================
class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['title', 'description', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder':'Prayer title','class':'form-control'}),
            'description': forms.Textarea(attrs={'placeholder':'Your prayer request','class':'form-control','rows':4}),
            'is_private': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
        labels = {
            'title': 'Prayer Title',
            'description': 'Prayer Request',
            'is_private': 'Private (only visible to leaders)',
        }


# ===========================
# Event Form
# ===========================
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# ===========================
# Media Item Form
# ===========================
class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['title', 'description', 'media_type', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
