"""
Communication views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def messages_list(request):
    """List all messages."""
    return render(request, 'communications/messages.html')


@login_required
@school_required
def send_message(request):
    """Send a message."""
    return render(request, 'communications/send.html')


@login_required
@school_required
def announcements(request):
    """List all announcements."""
    return render(request, 'communications/announcements.html')
