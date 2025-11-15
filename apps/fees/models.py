"""
Fee and finance models.
"""
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import shortuuid


class FeeStructure(models.Model):
    """Fee structure for classes."""

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    name = models.CharField(_('fee name'), max_length=200)  # e.g., "Tuition Fee", "Library Fee"
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    class_obj = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        blank=True,
        null=True
    )
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    description = models.TextField(_('description'), blank=True)
    is_mandatory = models.BooleanField(_('is mandatory'), default=True)
    due_date = models.DateField(_('due date'), blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('fee structure')
        verbose_name_plural = _('fee structures')
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'academic_year']),
        ]

    def __str__(self):
        return f'{self.name} - {self.amount}'


class StudentFee(models.Model):
    """Individual student fee records."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PARTIAL = 'partial', _('Partially Paid')
        PAID = 'paid', _('Paid')
        OVERDUE = 'overdue', _('Overdue')
        WAIVED = 'waived', _('Waived')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='student_fees'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='student_fees'
    )
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount_reason = models.CharField(_('discount reason'), max_length=200, blank=True)
    amount_paid = models.DecimalField(
        _('amount paid'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    due_date = models.DateField(_('due date'))

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('student fee')
        verbose_name_plural = _('student fees')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['status', 'due_date']),
        ]

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.fee_structure.name}'

    def get_balance(self):
        """Calculate remaining balance."""
        return self.total_amount - self.discount_amount - self.amount_paid

    def update_status(self):
        """Update payment status based on amount paid."""
        balance = self.get_balance()

        if balance <= 0:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        elif self.due_date < timezone.now().date():
            self.status = self.Status.OVERDUE
        else:
            self.status = self.Status.PENDING

        self.save(update_fields=['status'])


class Payment(models.Model):
    """Payment records."""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Cash')
        CARD = 'card', _('Card')
        BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
        ONLINE = 'online', _('Online Payment')
        PAYSTACK = 'paystack', _('Paystack')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethod.choices
    )
    transaction_reference = models.CharField(
        _('transaction reference'),
        max_length=200,
        unique=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Paystack specific fields
    paystack_reference = models.CharField(
        _('paystack reference'),
        max_length=200,
        blank=True
    )
    paystack_data = models.JSONField(_('paystack data'), default=dict, blank=True)

    # Payment details
    payment_date = models.DateTimeField(_('payment date'), default=timezone.now)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_payments'
    )
    remarks = models.TextField(_('remarks'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student_fee', 'status']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['-payment_date']),
        ]

    def __str__(self):
        return f'{self.transaction_reference} - {self.amount}'

    def complete_payment(self):
        """Mark payment as completed and update student fee."""
        self.status = self.Status.COMPLETED
        self.save()

        # Update student fee
        student_fee = self.student_fee
        student_fee.amount_paid += self.amount
        student_fee.save()
        student_fee.update_status()


class Receipt(models.Model):
    """Payment receipt."""

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(_('receipt number'), max_length=50, unique=True)
    generated_at = models.DateTimeField(_('generated at'), auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_receipts'
    )

    class Meta:
        verbose_name = _('receipt')
        verbose_name_plural = _('receipts')
        ordering = ['-generated_at']

    def __str__(self):
        return f'Receipt #{self.receipt_number}'


class FeeReminder(models.Model):
    """Fee payment reminders."""

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    sent_date = models.DateTimeField(_('sent date'), auto_now_add=True)
    reminder_type = models.CharField(
        _('reminder type'),
        max_length=20,
        choices=[
            ('email', _('Email')),
            ('sms', _('SMS')),
            ('both', _('Both'))
        ],
        default='email'
    )
    message = models.TextField(_('message'))
    is_sent = models.BooleanField(_('is sent'), default=False)

    class Meta:
        verbose_name = _('fee reminder')
        verbose_name_plural = _('fee reminders')
        ordering = ['-sent_date']

    def __str__(self):
        return f'Reminder for {self.student_fee.student.get_full_name()}'
