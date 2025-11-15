"""
Academic forms.
"""
from django import forms
from .models import Class, Subject, ClassSubject, Exam, ExamSubject, Grade, Assignment


class ClassForm(forms.ModelForm):
    """Form for creating/editing classes."""

    class Meta:
        model = Class
        fields = ['name', 'section', 'academic_year', 'class_teacher', 'room_number', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'section': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'academic_year': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'class_teacher': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'room_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class SubjectForm(forms.ModelForm):
    """Form for creating/editing subjects."""

    class Meta:
        model = Subject
        fields = ['name', 'code', 'subject_type', 'description', 'pass_mark', 'total_mark']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'subject_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'pass_mark': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'total_mark': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class ExamForm(forms.ModelForm):
    """Form for creating/editing exams."""

    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'term', 'start_date', 'end_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'exam_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'term': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class ExamSubjectForm(forms.ModelForm):
    """Form for adding subjects to exams."""

    class Meta:
        model = ExamSubject
        fields = ['subject', 'class_obj', 'exam_date', 'start_time', 'end_time', 'total_marks', 'pass_marks']
        widgets = {
            'subject': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'class_obj': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'exam_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'total_marks': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'pass_marks': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class GradeForm(forms.ModelForm):
    """Form for entering grades."""

    class Meta:
        model = Grade
        fields = ['student', 'marks_obtained', 'is_absent', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'is_absent': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class AssignmentForm(forms.ModelForm):
    """Form for creating assignments."""

    class Meta:
        model = Assignment
        fields = ['class_subject', 'title', 'description', 'due_date', 'total_marks', 'attachment', 'status']
        widgets = {
            'class_subject': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'total_marks': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }
