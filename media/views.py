# media/views.py
from django.shortcuts import render
from .models import MediaItem

def media_list(request):
    media_items = MediaItem.objects.all()
    return render(request, 'media/media_list.html', {'media_items': media_items})
