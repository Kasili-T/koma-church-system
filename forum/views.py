# forum/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Forum, Topic, Post

def forum_list(request):
    forums = Forum.objects.all()
    return render(request, "forum/forum_list.html", {"forums": forums})

def topic_list(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    return render(request, "forum/topic_list.html", {"forum": forum})

@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Post.objects.create(topic=topic, author=request.user, content=content)
            return redirect("topic_detail", topic_id=topic.id)
    return render(request, "forum/topic_detail.html", {"topic": topic})
