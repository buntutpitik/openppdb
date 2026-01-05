from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """
    Cek apakah user punya role (Django Group)
    Usage:
    {% if user|has_role:"ADMIN" %}
    """
    if not user.is_authenticated:
        return False

    return user.groups.filter(name=role_name).exists()
