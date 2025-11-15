"""
Fees admin.
"""
from django.contrib import admin
from .models import FeeStructure, StudentFee, Payment, Receipt, FeeReminder


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'academic_year', 'amount', 'is_mandatory']
    list_filter = ['school', 'academic_year', 'is_mandatory']


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'total_amount', 'amount_paid', 'status']
    list_filter = ['status']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_reference', 'student_fee', 'amount', 'payment_method', 'status']
    list_filter = ['payment_method', 'status']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment', 'generated_at']


@admin.register(FeeReminder)
class FeeReminderAdmin(admin.ModelAdmin):
    list_display = ['student_fee', 'reminder_type', 'sent_date', 'is_sent']
    list_filter = ['reminder_type', 'is_sent']
