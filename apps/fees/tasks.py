"""
Celery tasks for fee management.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import StudentFee, FeeReminder
from .utils import generate_fee_reminder_message


@shared_task
def send_fee_reminders():
    """Send fee reminders for overdue payments."""
    from apps.communications.models import EmailLog, SMSLog

    # Get all overdue fees
    overdue_fees = StudentFee.objects.filter(
        status__in=['pending', 'partial'],
        due_date__lt=timezone.now().date()
    ).select_related('student', 'student__school', 'fee_structure')

    count = 0
    for student_fee in overdue_fees:
        # Check if reminder was sent recently (within last 7 days)
        recent_reminder = FeeReminder.objects.filter(
            student_fee=student_fee,
            sent_date__gte=timezone.now() - timezone.timedelta(days=7)
        ).exists()

        if not recent_reminder:
            # Generate reminder message
            message = generate_fee_reminder_message(student_fee)

            # Get parent/guardian email and phone
            guardians = student_fee.student.student_guardians.filter(
                is_primary=True
            ).select_related('guardian')

            for sg in guardians:
                guardian = sg.guardian

                # Send email
                try:
                    send_mail(
                        subject=f'Fee Payment Reminder - {student_fee.student.school.name}',
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[guardian.email],
                        fail_silently=False,
                    )

                    EmailLog.objects.create(
                        school=student_fee.student.school,
                        recipient_email=guardian.email,
                        recipient_name=guardian.get_full_name(),
                        subject=f'Fee Payment Reminder',
                        body=message,
                        status='sent',
                        sent_at=timezone.now()
                    )
                except Exception as e:
                    EmailLog.objects.create(
                        school=student_fee.student.school,
                        recipient_email=guardian.email,
                        recipient_name=guardian.get_full_name(),
                        subject=f'Fee Payment Reminder',
                        body=message,
                        status='failed',
                        error_message=str(e)
                    )

            # Create reminder record
            FeeReminder.objects.create(
                student_fee=student_fee,
                reminder_type='email',
                message=message,
                is_sent=True
            )

            count += 1

    return f'Sent {count} fee reminders'


@shared_task
def update_overdue_fees():
    """Update status of overdue fees."""
    updated = StudentFee.objects.filter(
        status='pending',
        due_date__lt=timezone.now().date()
    ).update(status='overdue')

    return f'Updated {updated} overdue fees'


@shared_task
def process_paystack_webhook(event_type, data):
    """Process Paystack webhook events."""
    from .models import Payment
    from .utils import PaystackAPI

    if event_type == 'charge.success':
        reference = data.get('reference')

        try:
            payment = Payment.objects.get(transaction_reference=reference)

            # Verify transaction with Paystack
            paystack = PaystackAPI()
            verification = paystack.verify_transaction(reference)

            if verification.get('status') and verification['data']['status'] == 'success':
                payment.status = Payment.Status.COMPLETED
                payment.paystack_data = verification['data']
                payment.save()

                # Complete payment (updates student fee)
                payment.complete_payment()

                return f'Payment {reference} processed successfully'
            else:
                payment.status = Payment.Status.FAILED
                payment.save()
                return f'Payment {reference} verification failed'

        except Payment.DoesNotExist:
            return f'Payment with reference {reference} not found'

    return f'Unhandled event type: {event_type}'
