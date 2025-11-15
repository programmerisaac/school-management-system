"""
Parent views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def parent_portal(request):
    """Parent portal dashboard."""
    return render(request, 'parents/portal.html')


@login_required
@school_required
def children_list(request):
    """List of children."""
    return render(request, 'parents/children.html')


@login_required
@school_required
def child_detail(request, student_id):
    """Child detail view."""
    return render(request, 'parents/child_detail.html')
