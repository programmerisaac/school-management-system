"""
Celery tasks for communications.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task
def send_email_notification(recipient_email, recipient_name, subject, body, school_id):
    """Send email notification."""
    from .models import EmailLog

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        EmailLog.objects.create(
            school_id=school_id,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body=body,
            status='sent',
            sent_at=timezone.now()
        )

        return f'Email sent to {recipient_email}'
    except Exception as e:
        EmailLog.objects.create(
            school_id=school_id,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body=body,
            status='failed',
            error_message=str(e)
        )

        return f'Email failed: {str(e)}'


@shared_task
def send_sms_notification(recipient_phone, recipient_name, message, school_id):
    """Send SMS notification using Twilio."""
    from .models import SMSLog
    from twilio.rest import Client

    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return 'Twilio not configured'

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        sms = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=recipient_phone
        )

        SMSLog.objects.create(
            school_id=school_id,
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            message=message,
            status='sent',
            provider_response={'sid': sms.sid, 'status': sms.status},
            sent_at=timezone.now()
        )

        return f'SMS sent to {recipient_phone}'
    except Exception as e:
        SMSLog.objects.create(
            school_id=school_id,
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            message=message,
            status='failed',
            provider_response={'error': str(e)}
        )

        return f'SMS failed: {str(e)}'


@shared_task
def publish_announcement(announcement_id):
    """Publish announcement and send notifications."""
    from .models import Announcement, Notification
    from apps.accounts.models import User

    try:
        announcement = Announcement.objects.get(id=announcement_id)

        # Get target users
        users = []

        if announcement.target_all:
            users = User.objects.filter(
                school_memberships__school=announcement.school,
                is_active=True
            )
        else:
            # Build filter based on target audience
            if announcement.target_students:
                users.extend(User.objects.filter(role='student'))
            if announcement.target_parents:
                users.extend(User.objects.filter(role='parent'))
            if announcement.target_staff:
                users.extend(User.objects.filter(role__in=['teacher', 'staff']))

        # Create in-app notifications
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=announcement.title,
                    message=announcement.content[:500],
                    notification_type='info',
                    link=f'/communications/announcements/{announcement.id}/'
                )
            )

        Notification.objects.bulk_create(notifications)

        # Send emails if enabled
        if announcement.send_email:
            for user in users:
                send_email_notification.delay(
                    user.email,
                    user.get_full_name(),
                    announcement.title,
                    announcement.content,
                    str(announcement.school.id)
                )

        announcement.publish_date = timezone.now()
        announcement.status = 'published'
        announcement.save()

        return f'Published announcement to {len(users)} users'
    except Announcement.DoesNotExist:
        return 'Announcement not found'
