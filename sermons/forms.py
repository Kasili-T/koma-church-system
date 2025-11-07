from django import forms
from .models import Sermon

class SermonForm(forms.ModelForm):
    class Meta:
        model = Sermon
        fields = ['title', 'preacher', 'date', 'media_url', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
