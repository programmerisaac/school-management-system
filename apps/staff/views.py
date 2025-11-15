"""
Staff views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def staff_list(request):
    """List all staff members."""
    return render(request, 'staff/list.html')


@login_required
@school_required
def add_staff(request):
    """Add a new staff member."""
    return render(request, 'staff/add.html')


@login_required
@school_required
def staff_detail(request, pk):
    """Staff detail view."""
    return render(request, 'staff/detail.html')


@login_required
@school_required
def edit_staff(request, pk):
    """Edit staff view."""
    return render(request, 'staff/edit.html')


@login_required
@school_required
def staff_attendance(request):
    """Staff attendance view."""
    return render(request, 'staff/attendance.html')


@login_required
@school_required
def leave_requests(request):
    """Leave requests view."""
    return render(request, 'staff/leaves.html')
