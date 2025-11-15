"""
Core views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.core.decorators import school_required
from apps.core.cache_utils import CacheManager


@login_required
def dashboard(request):
    """Main dashboard view."""
    if not request.active_school:
        return redirect('schools:select')

    # Get cached school stats
    stats = CacheManager.get_school_stats(request.active_school.id)

    context = {
        'stats': stats,
    }
    return render(request, 'core/dashboard.html', context)


def landing_page(request):
    """Landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/landing.html')


# Error handlers
def error_404(request, exception):
    """404 error handler."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """500 error handler."""
    return render(request, 'errors/500.html', status=500)


def error_403(request, exception):
    """403 error handler."""
    return render(request, 'errors/403.html', status=403)
