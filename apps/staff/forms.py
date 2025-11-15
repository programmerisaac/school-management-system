"""
Staff forms.
"""
from django import forms
from .models import StaffMember, StaffAttendance, Leave


class StaffMemberForm(forms.ModelForm):
    """Form for creating/editing staff members."""

    class Meta:
        model = StaffMember
        fields = [
            'user', 'employee_id', 'staff_type', 'employment_type',
            'designation', 'department', 'joining_date', 'leaving_date',
            'qualifications', 'certifications', 'experience_years',
            'resume', 'id_document', 'subjects'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'employee_id': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'staff_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'employment_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'designation': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'department': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'leaving_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'qualifications': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'certifications': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'size': 5}),
        }


class LeaveRequestForm(forms.ModelForm):
    """Form for leave requests."""

    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class LeaveApprovalForm(forms.ModelForm):
    """Form for approving/rejecting leave."""

    class Meta:
        model = Leave
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'rejection_reason': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }
