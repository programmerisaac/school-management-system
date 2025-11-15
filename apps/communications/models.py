"""
Communication models for messages, announcements, and notifications.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import shortuuid


class Message(models.Model):
    """Message model for internal messaging."""

    class MessageType(models.TextChoices):
        DIRECT = 'direct', _('Direct Message')
        GROUP = 'group', _('Group Message')
        BROADCAST = 'broadcast', _('Broadcast')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_messages'
    )
    message_type = models.CharField(
        _('message type'),
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.DIRECT
    )
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    attachment = models.FileField(
        _('attachment'),
        upload_to='messages/attachments/',
        blank=True,
        null=True
    )
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f'{self.sender.get_full_name()} - {self.subject}'


class Announcement(models.Model):
    """Announcement model for school-wide or class-specific announcements."""

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        ARCHIVED = 'archived', _('Archived')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_announcements'
    )
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # Target audience
    target_all = models.BooleanField(_('target all'), default=True)
    target_students = models.BooleanField(_('target students'), default=False)
    target_parents = models.BooleanField(_('target parents'), default=False)
    target_staff = models.BooleanField(_('target staff'), default=False)
    target_classes = models.ManyToManyField(
        'academics.Class',
        blank=True,
        related_name='announcements'
    )

    # Notification settings
    send_email = models.BooleanField(_('send email notification'), default=False)
    send_sms = models.BooleanField(_('send SMS notification'), default=False)
    email_sent = models.BooleanField(_('email sent'), default=False)
    sms_sent = models.BooleanField(_('SMS sent'), default=False)

    # Dates
    publish_date = models.DateTimeField(_('publish date'), blank=True, null=True)
    expire_date = models.DateTimeField(_('expire date'), blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('announcement')
        verbose_name_plural = _('announcements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'status', '-created_at']),
        ]

    def __str__(self):
        return self.title


class Notification(models.Model):
    """Notification model for system notifications."""

    class NotificationType(models.TextChoices):
        INFO = 'info', _('Information')
        SUCCESS = 'success', _('Success')
        WARNING = 'warning', _('Warning')
        ERROR = 'error', _('Error')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    notification_type = models.CharField(
        _('type'),
        max_length=10,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    link = models.CharField(_('link'), max_length=500, blank=True)
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.title}'

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class SMSLog(models.Model):
    """Log of SMS messages sent."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        FAILED = 'failed', _('Failed')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='sms_logs'
    )
    recipient_phone = models.CharField(_('recipient phone'), max_length=20)
    recipient_name = models.CharField(_('recipient name'), max_length=200, blank=True)
    message = models.TextField(_('message'))
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    provider_response = models.JSONField(_('provider response'), default=dict, blank=True)
    cost = models.DecimalField(_('cost'), max_digits=10, decimal_places=4, default=0)
    sent_at = models.DateTimeField(_('sent at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('SMS log')
        verbose_name_plural = _('SMS logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'SMS to {self.recipient_phone} - {self.status}'


class EmailLog(models.Model):
    """Log of emails sent."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        FAILED = 'failed', _('Failed')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='email_logs'
    )
    recipient_email = models.EmailField(_('recipient email'))
    recipient_name = models.CharField(_('recipient name'), max_length=200, blank=True)
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField(_('error message'), blank=True)
    sent_at = models.DateTimeField(_('sent at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('email log')
        verbose_name_plural = _('email logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Email to {self.recipient_email} - {self.status}'
