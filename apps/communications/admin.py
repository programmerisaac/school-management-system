"""
Communications admin.
"""
from django.contrib import admin
from .models import Message, Announcement, Notification, SMSLog, EmailLog


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'subject', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['subject', 'body', 'sender__email']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'author', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status', 'school']
    search_fields = ['title', 'content']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'recipient_name', 'status', 'cost', 'sent_at']
    list_filter = ['status', 'school']
    search_fields = ['recipient_phone', 'recipient_name', 'message']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'recipient_name', 'subject', 'status', 'sent_at']
    list_filter = ['status', 'school']
    search_fields = ['recipient_email', 'recipient_name', 'subject']
