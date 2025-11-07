from django import template

register = template.Library()

@register.filter
def reacted_by(prayer_request, user):
    """
    Returns True if the user has reacted (prayed) for the request.
    """
    return prayer_request.reactions.filter(user=user).exists()
