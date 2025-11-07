# chat/management/commands/create_default_rooms.py

from django.core.management.base import BaseCommand
from chat.models import ChatRoom
from django.contrib.auth.models import User
from accounts.models import Role  # if you have a Role model
from chat.default_rooms import DEFAULT_ROOMS

class Command(BaseCommand):
    help = "Create default chat rooms and assign users based on roles"

    def handle(self, *args, **options):
        for room_info in DEFAULT_ROOMS:
            room, created = ChatRoom.objects.get_or_create(name=room_info["name"])
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created room: {room.name}"))

            # Add users by role or everyone if roles list empty
            if room_info["roles"]:
                for role_name in room_info["roles"]:
                    users = User.objects.filter(member__role__name=role_name)
                    for user in users:
                        room.participants.add(user)
            else:
                # Everyone
                for user in User.objects.all():
                    room.participants.add(user)

        self.stdout.write(self.style.SUCCESS("Default rooms setup completed."))
