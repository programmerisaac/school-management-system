"""
Fee forms.
"""
from django import forms
from .models import FeeStructure, StudentFee, Payment


class FeeStructureForm(forms.ModelForm):
    """Form for creating/editing fee structures."""

    class Meta:
        model = FeeStructure
        fields = ['name', 'academic_year', 'class_obj', 'amount', 'description', 'is_mandatory', 'due_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'academic_year': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'class_obj': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class StudentFeeForm(forms.ModelForm):
    """Form for assigning fees to students."""

    class Meta:
        model = StudentFee
        fields = ['student', 'fee_structure', 'total_amount', 'discount_amount', 'discount_reason', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'fee_structure': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'total_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'discount_reason': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments."""

    class Meta:
        model = Payment
        fields = ['student_fee', 'amount', 'payment_method', 'transaction_reference', 'remarks']
        widgets = {
            'student_fee': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }
