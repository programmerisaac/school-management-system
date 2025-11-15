"""
Celery configuration for the School Management System.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('school_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-fee-reminders': {
        'task': 'apps.fees.tasks.send_fee_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'generate-attendance-reports': {
        'task': 'apps.students.tasks.generate_attendance_reports',
        'schedule': crontab(hour=22, minute=0, day_of_week='sunday'),  # Every Sunday at 10 PM
    },
    'check-subscription-expiry': {
        'task': 'apps.schools.tasks.check_subscription_expiry',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
