"""
User and authentication models.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import shortuuid


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email as the unique identifier."""

    class UserRole(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('Super Admin')  # Platform owner
        SCHOOL_OWNER = 'school_owner', _('School Owner')  # Can own multiple schools
        SCHOOL_ADMIN = 'school_admin', _('School Admin')  # School administrator
        PRINCIPAL = 'principal', _('Principal')
        TEACHER = 'teacher', _('Teacher')
        STAFF = 'staff', _('Staff')
        PARENT = 'parent', _('Parent')
        STUDENT = 'student', _('Student')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.SCHOOL_OWNER
    )
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profiles/',
        blank=True,
        null=True
    )

    # Status fields
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)

    # Timestamps
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['-date_joined']),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def get_schools(self):
        """Get all schools this user has access to (cached)."""
        cache_key = f'user_schools_{self.id}'
        schools = cache.get(cache_key)

        if schools is None:
            if self.role == self.UserRole.SUPER_ADMIN:
                from apps.schools.models import School
                schools = School.objects.all()
            elif self.role == self.UserRole.SCHOOL_OWNER:
                schools = self.owned_schools.filter(is_active=True)
            else:
                schools = self.school_memberships.filter(
                    school__is_active=True
                ).select_related('school').values_list('school', flat=True)
                from apps.schools.models import School
                schools = School.objects.filter(id__in=schools)

            # Cache for 5 minutes
            cache.set(cache_key, list(schools), 300)

        return schools

    def invalidate_cache(self):
        """Invalidate all cache keys for this user."""
        cache_keys = [
            f'user_schools_{self.id}',
            f'user_permissions_{self.id}',
            f'user_active_school_{self.id}',
        ]
        cache.delete_many(cache_keys)

    def save(self, *args, **kwargs):
        """Override save to invalidate cache."""
        super().save(*args, **kwargs)
        self.invalidate_cache()


class UserProfile(models.Model):
    """Extended user profile information."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other'))
        ],
        blank=True
    )
    emergency_contact_name = models.CharField(
        _('emergency contact name'),
        max_length=200,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        _('emergency contact phone'),
        max_length=20,
        blank=True
    )
    bio = models.TextField(_('bio'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f'{self.user.get_full_name()} Profile'


class ActivityLog(models.Model):
    """Log user activities for audit trail."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    action = models.CharField(_('action'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('activity log')
        verbose_name_plural = _('activity logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.user} - {self.action} at {self.created_at}'
