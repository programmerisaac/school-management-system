"""
School views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.core.decorators import role_required
from apps.schools.models import School


@login_required
def school_list(request):
    """List all schools for the user."""
    schools = request.user.get_schools()
    return render(request, 'schools/list.html', {'schools': schools})


@login_required
def select_school(request):
    """School selection page."""
    schools = request.user.get_schools()
    return render(request, 'schools/select.html', {'schools': schools})


@login_required
@role_required('school_owner', 'super_admin')
def create_school(request):
    """Create a new school."""
    return render(request, 'schools/create.html')


@login_required
def school_detail(request, pk):
    """School detail view."""
    school = get_object_or_404(School, pk=pk)
    return render(request, 'schools/detail.html', {'school': school})


@login_required
def edit_school(request, pk):
    """Edit school view."""
    school = get_object_or_404(School, pk=pk)
    return render(request, 'schools/edit.html', {'school': school})


@login_required
def school_settings(request, pk):
    """School settings view."""
    school = get_object_or_404(School, pk=pk)
    return render(request, 'schools/settings.html', {'school': school})


@login_required
def subscription(request):
    """Subscription management view."""
    return render(request, 'schools/subscription.html')
