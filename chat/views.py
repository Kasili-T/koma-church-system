from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

@login_required
def chat_rooms_view(request):
    """List all chat rooms the user participates in."""
    rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, "chat/rooms.html", {"rooms": rooms})

@login_required
def chat_room(request, room_name):
    """Renders a chat room by name with past messages."""
    room = get_object_or_404(ChatRoom, name=room_name)
    messages = room.messages.order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            Message.objects.create(room=room, sender=request.user, content=content)
        return redirect("chat:chat_room", room_name=room.name)

    context = {
        "room": room,
        "messages": messages
    }
    return render(request, "chat/room.html", context)
