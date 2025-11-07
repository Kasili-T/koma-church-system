from django.shortcuts import render, get_object_or_404, redirect
from .models import Sermon
from .forms import SermonForm

# List sermons
def sermons_list(request):
    sermons = Sermon.objects.all().order_by('-date')
    return render(request, "sermons/sermons.html", {"sermons": sermons})

# Create sermon
def sermon_create(request):
    if request.method == "POST":
        form = SermonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sermons:sermons_list")
    else:
        form = SermonForm()
    return render(request, "sermons/sermon_form.html", {"form": form})

# Update sermon
def sermon_update(request, id):
    sermon = get_object_or_404(Sermon, id=id)
    if request.method == "POST":
        form = SermonForm(request.POST, instance=sermon)
        if form.is_valid():
            form.save()
            return redirect("sermons:sermons_list")
    else:
        form = SermonForm(instance=sermon)
    return render(request, "sermons/sermon_form.html", {"form": form})

# Delete sermon
def sermon_delete(request, id):
    sermon = get_object_or_404(Sermon, id=id)
    if request.method == "POST":
        sermon.delete()
        return redirect("sermons:sermons_list")
    return render(request, "sermons/sermon_confirm_delete.html", {"sermon": sermon})
