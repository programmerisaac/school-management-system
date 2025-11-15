"""
Fees signals.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment


@receiver(post_save, sender=Payment)
def update_student_fee_on_payment(sender, instance, created, **kwargs):
    """Update student fee when payment is completed."""
    if instance.status == Payment.Status.COMPLETED and created:
        instance.complete_payment()
