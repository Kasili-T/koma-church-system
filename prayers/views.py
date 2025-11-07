from django.shortcuts import render

def prayer_requests(request):
    return render(request, "prayers/requests.html")
