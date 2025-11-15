"""
Context processors for adding variables to templates.
"""
from django.conf import settings


def school_context(request):
    """Add active school to context."""
    context = {
        'active_school': getattr(request, 'active_school', None),
    }

    # Add user's schools if authenticated
    if request.user.is_authenticated:
        context['user_schools'] = request.user.get_schools()
    else:
        context['user_schools'] = []

    return context


def theme_context(request):
    """Add theme colors to context."""
    active_school = getattr(request, 'active_school', None)

    if active_school:
        primary_color = active_school.primary_color
        secondary_color = active_school.secondary_color
    else:
        primary_color = settings.PRIMARY_COLOR
        secondary_color = settings.SECONDARY_COLOR

    return {
        'primary_color': primary_color,
        'secondary_color': secondary_color,
    }
