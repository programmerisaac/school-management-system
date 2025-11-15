"""
Academic views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import school_required


@login_required
@school_required
def class_list(request):
    """List all classes."""
    return render(request, 'academics/class_list.html')


@login_required
@school_required
def add_class(request):
    """Add a new class."""
    return render(request, 'academics/add_class.html')


@login_required
@school_required
def subject_list(request):
    """List all subjects."""
    return render(request, 'academics/subject_list.html')


@login_required
@school_required
def add_subject(request):
    """Add a new subject."""
    return render(request, 'academics/add_subject.html')


@login_required
@school_required
def exam_list(request):
    """List all exams."""
    return render(request, 'academics/exam_list.html')


@login_required
@school_required
def add_exam(request):
    """Add a new exam."""
    return render(request, 'academics/add_exam.html')


@login_required
@school_required
def exam_detail(request, pk):
    """Exam detail view."""
    return render(request, 'academics/exam_detail.html')


@login_required
@school_required
def enter_grades(request, pk):
    """Enter grades for an exam."""
    return render(request, 'academics/enter_grades.html')


@login_required
@school_required
def assignment_list(request):
    """List all assignments."""
    return render(request, 'academics/assignment_list.html')


@login_required
@school_required
def add_assignment(request):
    """Add a new assignment."""
    return render(request, 'academics/add_assignment.html')
