"""
Staff models.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import shortuuid


class StaffMember(models.Model):
    """Staff member model."""

    class StaffType(models.TextChoices):
        TEACHING = 'teaching', _('Teaching Staff')
        NON_TEACHING = 'non_teaching', _('Non-Teaching Staff')
        ADMINISTRATIVE = 'administrative', _('Administrative Staff')

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', _('Full Time')
        PART_TIME = 'part_time', _('Part Time')
        CONTRACT = 'contract', _('Contract')
        TEMPORARY = 'temporary', _('Temporary')

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ON_LEAVE = 'on_leave', _('On Leave')
        SUSPENDED = 'suspended', _('Suspended')
        TERMINATED = 'terminated', _('Terminated')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='staff_members'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        limit_choices_to={'role__in': ['teacher', 'staff', 'school_admin', 'principal']}
    )

    # Employee Information
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True)
    staff_type = models.CharField(
        _('staff type'),
        max_length=20,
        choices=StaffType.choices,
        default=StaffType.TEACHING
    )
    employment_type = models.CharField(
        _('employment type'),
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )
    designation = models.CharField(_('designation'), max_length=200)
    department = models.CharField(_('department'), max_length=200, blank=True)

    # Dates
    joining_date = models.DateField(_('joining date'))
    leaving_date = models.DateField(_('leaving date'), blank=True, null=True)

    # Qualifications
    qualifications = models.TextField(_('qualifications'), blank=True)
    certifications = models.TextField(_('certifications'), blank=True)
    experience_years = models.IntegerField(_('years of experience'), default=0)

    # Documents
    resume = models.FileField(_('resume'), upload_to='staff/resumes/', blank=True, null=True)
    id_document = models.FileField(
        _('ID document'),
        upload_to='staff/documents/',
        blank=True,
        null=True
    )

    # Subjects (for teachers)
    subjects = models.ManyToManyField(
        'academics.Subject',
        blank=True,
        related_name='teachers',
        verbose_name=_('subjects taught')
    )

    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('staff member')
        verbose_name_plural = _('staff members')
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.employee_id})'


class StaffAttendance(models.Model):
    """Staff attendance records."""

    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')
        HALF_DAY = 'half_day', _('Half Day')
        ON_LEAVE = 'on_leave', _('On Leave')

    staff = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(_('date'))
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT
    )
    check_in_time = models.TimeField(_('check-in time'), blank=True, null=True)
    check_out_time = models.TimeField(_('check-out time'), blank=True, null=True)
    remarks = models.TextField(_('remarks'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('staff attendance')
        verbose_name_plural = _('staff attendance records')
        unique_together = ['staff', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['staff', '-date']),
        ]

    def __str__(self):
        return f'{self.staff.user.get_full_name()} - {self.date} ({self.status})'


class Leave(models.Model):
    """Leave requests for staff."""

    class LeaveType(models.TextChoices):
        SICK = 'sick', _('Sick Leave')
        CASUAL = 'casual', _('Casual Leave')
        ANNUAL = 'annual', _('Annual Leave')
        MATERNITY = 'maternity', _('Maternity Leave')
        PATERNITY = 'paternity', _('Paternity Leave')
        UNPAID = 'unpaid', _('Unpaid Leave')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        CANCELLED = 'cancelled', _('Cancelled')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    staff = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(
        _('leave type'),
        max_length=20,
        choices=LeaveType.choices
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    reason = models.TextField(_('reason'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approval_date = models.DateTimeField(_('approval date'), blank=True, null=True)
    rejection_reason = models.TextField(_('rejection reason'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('leave')
        verbose_name_plural = _('leaves')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['staff', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.staff.user.get_full_name()} - {self.leave_type} ({self.start_date})'

    def get_total_days(self):
        """Calculate total days of leave."""
        return (self.end_date - self.start_date).days + 1
