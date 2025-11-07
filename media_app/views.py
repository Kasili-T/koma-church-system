from django.shortcuts import render, get_object_or_404
from .models import MediaItem

def media_list(request):
    items = MediaItem.objects.all().order_by('-uploaded_at')
    return render(request, 'media_app/media_list.html', {'items': items})

def media_detail(request, pk):
    item = get_object_or_404(MediaItem, pk=pk)
    return render(request, 'media_app/media_detail.html', {'item': item})
