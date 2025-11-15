"""
Schools signals.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import School, SchoolMembership


@receiver(post_save, sender=School)
def create_school_owner_membership(sender, instance, created, **kwargs):
    """Create membership for school owner when school is created."""
    if created:
        SchoolMembership.objects.get_or_create(
            school=instance,
            user=instance.owner,
            defaults={
                'role': 'admin',
                'can_manage_students': True,
                'can_manage_staff': True,
                'can_manage_fees': True,
                'can_manage_exams': True,
            }
        )
