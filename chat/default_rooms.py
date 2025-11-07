# chat/default_rooms.py

DEFAULT_ROOMS = [
    {"name": "General", "roles": []},          # Everyone
    {"name": "Prayer", "roles": ["Member"]},   # Only members
    {"name": "Events", "roles": ["Treasury", "Admin"]},  # Event-related roles
    {"name": "Announcements", "roles": []},    # Everyone
]
