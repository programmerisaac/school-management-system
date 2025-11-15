"""
Academics admin.
"""
from django.contrib import admin
from .models import (
    Class, Subject, ClassSubject, Exam,
    ExamSubject, Grade, Assignment, AssignmentSubmission
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'school', 'academic_year', 'class_teacher']
    list_filter = ['school', 'academic_year']
    search_fields = ['name', 'section']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subject_type', 'school']
    list_filter = ['subject_type', 'school']
    search_fields = ['name', 'code']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'subject', 'teacher']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'school', 'term', 'start_date', 'end_date']
    list_filter = ['exam_type', 'school']


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ['exam', 'subject', 'class_obj', 'exam_date']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_subject', 'marks_obtained', 'grade']
    list_filter = ['grade', 'is_absent']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_subject', 'due_date', 'status']
    list_filter = ['status']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'is_late']
    list_filter = ['is_late']
