"""
Student views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def student_list(request):
    """List all students."""
    return render(request, 'students/list.html')


@login_required
@school_required
def add_student(request):
    """Add a new student."""
    return render(request, 'students/add.html')


@login_required
@school_required
def student_detail(request, pk):
    """Student detail view."""
    return render(request, 'students/detail.html')


@login_required
@school_required
def edit_student(request, pk):
    """Edit student view."""
    return render(request, 'students/edit.html')


@login_required
@school_required
def student_attendance(request, pk):
    """Student attendance view."""
    return render(request, 'students/attendance.html')


@login_required
@school_required
def student_grades(request, pk):
    """Student grades view."""
    return render(request, 'students/grades.html')


@login_required
@school_required
def mark_attendance(request):
    """Mark attendance view."""
    return render(request, 'students/mark_attendance.html')
