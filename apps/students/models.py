"""
Student models.
"""
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _
import shortuuid
import qrcode
from io import BytesIO
from django.core.files import File


class Student(models.Model):
    """Student model."""

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', _('A+')
        A_NEG = 'A-', _('A-')
        B_POS = 'B+', _('B+')
        B_NEG = 'B-', _('B-')
        AB_POS = 'AB+', _('AB+')
        AB_NEG = 'AB-', _('AB-')
        O_POS = 'O+', _('O+')
        O_NEG = 'O-', _('O-')

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        GRADUATED = 'graduated', _('Graduated')
        TRANSFERRED = 'transferred', _('Transferred')
        WITHDRAWN = 'withdrawn', _('Withdrawn')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='students'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True,
        blank=True,
        limit_choices_to={'role': 'student'}
    )

    # Basic Information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    middle_name = models.CharField(_('middle name'), max_length=150, blank=True)
    admission_number = models.CharField(_('admission number'), max_length=50, unique=True)
    date_of_birth = models.DateField(_('date of birth'))
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other'))
        ]
    )
    photo = models.ImageField(_('photo'), upload_to='students/photos/', blank=True, null=True)

    # Contact Information
    email = models.EmailField(_('email'), blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = models.CharField(_('country'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)

    # Academic Information
    current_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    admission_date = models.DateField(_('admission date'))
    previous_school = models.CharField(_('previous school'), max_length=255, blank=True)

    # Medical Information
    blood_group = models.CharField(
        _('blood group'),
        max_length=3,
        choices=BloodGroup.choices,
        blank=True
    )
    allergies = models.TextField(_('allergies'), blank=True)
    medical_conditions = models.TextField(_('medical conditions'), blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(_('emergency contact name'), max_length=200)
    emergency_contact_phone = models.CharField(_('emergency contact phone'), max_length=20)
    emergency_contact_relationship = models.CharField(
        _('emergency contact relationship'),
        max_length=100
    )

    # Special Needs
    special_needs = models.TextField(_('special needs'), blank=True)
    has_special_needs = models.BooleanField(_('has special needs'), default=False)

    # QR Code for ID Card
    qr_code = models.ImageField(
        _('QR code'),
        upload_to='students/qr_codes/',
        blank=True,
        null=True
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
        verbose_name = _('student')
        verbose_name_plural = _('students')
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['admission_number']),
            models.Index(fields=['current_class']),
            models.Index(fields=['school', 'current_class']),
        ]

    def __str__(self):
        return f'{self.get_full_name()} ({self.admission_number})'

    def get_full_name(self):
        """Get student's full name."""
        if self.middle_name:
            return f'{self.first_name} {self.middle_name} {self.last_name}'
        return f'{self.first_name} {self.last_name}'

    def generate_qr_code(self):
        """Generate QR code for student ID."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'{self.school.slug}/{self.admission_number}')
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        file_name = f'qr_{self.admission_number}.png'
        self.qr_code.save(file_name, File(buffer), save=False)

    def get_attendance_rate(self):
        """Get student attendance rate (cached)."""
        cache_key = f'student_attendance_{self.id}'
        rate = cache.get(cache_key)

        if rate is None:
            total = self.attendance_records.count()
            present = self.attendance_records.filter(status='present').count()
            rate = (present / total * 100) if total > 0 else 0
            cache.set(cache_key, rate, 3600)  # Cache for 1 hour

        return rate

    def save(self, *args, **kwargs):
        """Override save to generate QR code."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new or not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])


class Guardian(models.Model):
    """Parent/Guardian model."""

    class Relationship(models.TextChoices):
        FATHER = 'father', _('Father')
        MOTHER = 'mother', _('Mother')
        GUARDIAN = 'guardian', _('Guardian')
        OTHER = 'other', _('Other')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='guardian_profile',
        null=True,
        blank=True,
        limit_choices_to={'role': 'parent'}
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='guardians'
    )

    # Basic Information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    relationship = models.CharField(
        _('relationship'),
        max_length=20,
        choices=Relationship.choices
    )
    email = models.EmailField(_('email'))
    phone_number = models.CharField(_('phone number'), max_length=20)
    alternate_phone = models.CharField(_('alternate phone'), max_length=20, blank=True)

    # Address
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = models.CharField(_('country'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)

    # Professional Information
    occupation = models.CharField(_('occupation'), max_length=200, blank=True)
    employer = models.CharField(_('employer'), max_length=200, blank=True)
    work_phone = models.CharField(_('work phone'), max_length=20, blank=True)

    # Photo
    photo = models.ImageField(_('photo'), upload_to='guardians/photos/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('guardian')
        verbose_name_plural = _('guardians')
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['school', 'email']),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.relationship})'

    def get_full_name(self):
        """Get guardian's full name."""
        return f'{self.first_name} {self.last_name}'


class StudentGuardian(models.Model):
    """Relationship between students and guardians."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_guardians'
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name='guardian_students'
    )
    is_primary = models.BooleanField(_('is primary contact'), default=False)
    can_pickup = models.BooleanField(_('can pickup student'), default=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('student guardian')
        verbose_name_plural = _('student guardians')
        unique_together = ['student', 'guardian']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.guardian.get_full_name()}'


class Attendance(models.Model):
    """Student attendance records."""

    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')
        EXCUSED = 'excused', _('Excused')

    student = models.ForeignKey(
        Student,
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
    remarks = models.TextField(_('remarks'), blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances'
    )

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('attendance')
        verbose_name_plural = _('attendance records')
        unique_together = ['student', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', '-date']),
            models.Index(fields=['date', 'status']),
        ]

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.date} ({self.status})'
