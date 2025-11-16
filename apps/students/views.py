"""
Student views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from apps.core.decorators import school_required
from apps.core.utils import generate_admission_number
from .models import Student, Guardian, Attendance
from .forms import StudentForm
from apps.academics.models import Class


@login_required
@school_required
def student_list(request):
    """List all students."""
    students = Student.objects.filter(school=request.active_school)
    
    # Filters
    search = request.GET.get('search')
    class_id = request.GET.get('class')
    status = request.GET.get('status')
    
    if search:
        students = students.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(admission_number__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    if class_id:
        students = students.filter(current_class_id=class_id)
    
    if status:
        students = students.filter(status=status)
    
    students = students.select_related('current_class').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)
    
    # Get classes for filter
    classes = Class.objects.filter(school=request.active_school)
    
    context = {
        'students': students_page,
        'classes': classes,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': students_page,
    }
    
    return render(request, 'students/list.html', context)


@login_required
@school_required
def add_student(request):
    """Add a new student."""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.active_school
            
            # Generate admission number if not provided
            if not student.admission_number:
                school_code = request.active_school.slug[:3].upper()
                student.admission_number = generate_admission_number(school_code)
            
            student.save()
            messages.success(request, f'Student "{student.get_full_name()}" added successfully!')
            return redirect('students:detail', pk=student.id)
    else:
        form = StudentForm()
        # Filter current_class choices to current school
        form.fields['current_class'].queryset = Class.objects.filter(
            school=request.active_school
        )
    
    return render(request, 'students/add.html', {'form': form})


@login_required
@school_required
def student_detail(request, pk):
    """Student detail view."""
    student = get_object_or_404(
        Student.objects.select_related('school', 'current_class'),
        pk=pk,
        school=request.active_school
    )
    
    # Get guardians
    guardians = student.student_guardians.select_related('guardian').all()
    
    # Get recent attendance (last 30 days)
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_attendance = student.attendance_records.filter(
        date__gte=thirty_days_ago
    ).order_by('-date')[:10]
    
    # Calculate attendance summary
    from apps.students.utils import get_student_attendance_summary
    attendance_summary = get_student_attendance_summary(student)
    
    context = {
        'student': student,
        'guardians': guardians,
        'recent_attendance': recent_attendance,
        'attendance_summary': attendance_summary,
    }
    
    return render(request, 'students/detail.html', context)


@login_required
@school_required
def edit_student(request, pk):
    """Edit student view."""
    student = get_object_or_404(Student, pk=pk, school=request.active_school)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('students:detail', pk=pk)
    else:
        form = StudentForm(instance=student)
        form.fields['current_class'].queryset = Class.objects.filter(
            school=request.active_school
        )
    
    return render(request, 'students/edit.html', {'form': form, 'student': student})


@login_required
@school_required
def student_attendance(request, pk):
    """Student attendance view."""
    student = get_object_or_404(Student, pk=pk, school=request.active_school)
    attendance_records = student.attendance_records.order_by('-date')
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
    }
    
    return render(request, 'students/attendance.html', context)


@login_required
@school_required
def student_grades(request, pk):
    """Student grades view."""
    student = get_object_or_404(Student, pk=pk, school=request.active_school)
    grades = student.grades.select_related(
        'exam_subject__exam',
        'exam_subject__subject'
    ).order_by('-exam_subject__exam__start_date')
    
    context = {
        'student': student,
        'grades': grades,
    }
    
    return render(request, 'students/grades.html', context)


@login_required
@school_required
def mark_attendance(request):
    """Mark attendance view."""
    from .forms import BulkAttendanceForm
    
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            class_id = form.cleaned_data['class_id']
            
            students = Student.objects.filter(
                school=request.active_school,
                current_class_id=class_id,
                status='active'
            )
            
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                remarks = request.POST.get(f'remarks_{student.id}', '')
                
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date,
                        defaults={
                            'status': status,
                            'remarks': remarks,
                            'recorded_by': request.user
                        }
                    )
            
            messages.success(request, 'Attendance marked successfully!')
            return redirect('students:mark_attendance')
    else:
        form = BulkAttendanceForm()
    
    classes = Class.objects.filter(school=request.active_school)
    
    return render(request, 'students/mark_attendance.html', {
        'form': form,
        'classes': classes,
    })
