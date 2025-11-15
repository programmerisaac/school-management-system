"""
Account views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html')


@login_required
def edit_profile(request):
    """Edit profile view."""
    return render(request, 'accounts/edit_profile.html')


@login_required
def settings(request):
    """User settings view."""
    return render(request, 'accounts/settings.html')
