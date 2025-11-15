"""
School and subscription models.
"""
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import shortuuid


class School(models.Model):
    """School model representing a tenant school."""

    class SchoolType(models.TextChoices):
        PRIMARY = 'primary', _('Primary School')
        SECONDARY = 'secondary', _('Secondary School')
        HIGH = 'high', _('High School')
        COLLEGE = 'college', _('College')
        UNIVERSITY = 'university', _('University')
        MIXED = 'mixed', _('Mixed Levels')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    name = models.CharField(_('school name'), max_length=255)
    slug = models.SlugField(_('slug'), unique=True, max_length=255)
    school_type = models.CharField(
        _('school type'),
        max_length=20,
        choices=SchoolType.choices,
        default=SchoolType.MIXED
    )

    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_schools',
        limit_choices_to={'role': 'school_owner'}
    )

    # Contact Information
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20)
    website = models.URLField(_('website'), blank=True)

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=255)
    address_line2 = models.CharField(_('address line 2'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = models.CharField(_('country'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)

    # Branding
    logo = models.ImageField(_('logo'), upload_to='schools/logos/', blank=True, null=True)
    primary_color = models.CharField(
        _('primary color'),
        max_length=7,
        default='#154bba',
        help_text=_('Hex color code (e.g., #154bba)')
    )
    secondary_color = models.CharField(
        _('secondary color'),
        max_length=7,
        default='#f9d000',
        help_text=_('Hex color code (e.g., #f9d000)')
    )

    # Settings
    academic_year_start_month = models.IntegerField(
        _('academic year start month'),
        default=9,
        help_text=_('Month number (1-12)')
    )
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')

    # Subscription
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools'
    )

    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    is_verified = models.BooleanField(_('is verified'), default=False)

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('school')
        verbose_name_plural = _('schools')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def get_subscription_status(self):
        """Get the subscription status (cached)."""
        cache_key = f'school_subscription_{self.id}'
        status = cache.get(cache_key)

        if status is None:
            if not self.subscription:
                status = 'no_subscription'
            elif self.subscription.is_active():
                status = 'active'
            elif self.subscription.is_trial():
                status = 'trial'
            else:
                status = 'expired'

            cache.set(cache_key, status, 300)  # Cache for 5 minutes

        return status

    def invalidate_cache(self):
        """Invalidate all cache keys for this school."""
        cache_keys = [
            f'school_subscription_{self.id}',
            f'school_stats_{self.id}',
            f'school_members_{self.id}',
        ]
        cache.delete_many(cache_keys)

    def save(self, *args, **kwargs):
        """Override save to invalidate cache."""
        super().save(*args, **kwargs)
        self.invalidate_cache()


class SubscriptionPlan(models.Model):
    """Subscription plans available for schools."""

    name = models.CharField(_('plan name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)

    # Pricing
    monthly_price = models.DecimalField(
        _('monthly price'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    yearly_price = models.DecimalField(
        _('yearly price'),
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Limits
    max_students = models.IntegerField(
        _('max students'),
        default=100,
        help_text=_('Maximum number of students allowed')
    )
    max_staff = models.IntegerField(
        _('max staff'),
        default=10,
        help_text=_('Maximum number of staff members allowed')
    )

    # Features (JSON field for flexible feature toggling)
    features = models.JSONField(
        _('features'),
        default=dict,
        help_text=_('Feature flags for this plan')
    )

    # Trial
    trial_days = models.IntegerField(_('trial days'), default=14)

    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)

    # Ordering
    order = models.IntegerField(_('order'), default=0)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subscription plan')
        verbose_name_plural = _('subscription plans')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Subscription model for school payment tracking."""

    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', _('Monthly')
        YEARLY = 'yearly', _('Yearly')

    class Status(models.TextChoices):
        TRIAL = 'trial', _('Trial')
        ACTIVE = 'active', _('Active')
        EXPIRED = 'expired', _('Expired')
        CANCELLED = 'cancelled', _('Cancelled')
        SUSPENDED = 'suspended', _('Suspended')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    billing_cycle = models.CharField(
        _('billing cycle'),
        max_length=10,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY
    )

    # Dates
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    trial_end_date = models.DateTimeField(_('trial end date'), blank=True, null=True)

    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.TRIAL
    )
    auto_renew = models.BooleanField(_('auto renew'), default=True)

    # Payment
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    next_billing_date = models.DateTimeField(_('next billing date'), blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'end_date']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.plan.name} - {self.status}'

    def is_active(self):
        """Check if subscription is currently active."""
        return (
            self.status == self.Status.ACTIVE and
            self.end_date > timezone.now()
        )

    def is_trial(self):
        """Check if subscription is in trial period."""
        return (
            self.status == self.Status.TRIAL and
            self.trial_end_date and
            self.trial_end_date > timezone.now()
        )

    def days_remaining(self):
        """Get number of days remaining in subscription."""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0


class SchoolMembership(models.Model):
    """Membership model for users in schools."""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        PRINCIPAL = 'principal', _('Principal')
        TEACHER = 'teacher', _('Teacher')
        STAFF = 'staff', _('Staff')

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='school_memberships'
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF
    )

    # Permissions (can be extended with django-guardian for object-level perms)
    can_manage_students = models.BooleanField(_('can manage students'), default=False)
    can_manage_staff = models.BooleanField(_('can manage staff'), default=False)
    can_manage_fees = models.BooleanField(_('can manage fees'), default=False)
    can_manage_exams = models.BooleanField(_('can manage exams'), default=False)

    # Status
    is_active = models.BooleanField(_('is active'), default=True)

    # Timestamps
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('school membership')
        verbose_name_plural = _('school memberships')
        unique_together = ['school', 'user']
        indexes = [
            models.Index(fields=['school', 'user']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.school.name} ({self.role})'


class AcademicYear(models.Model):
    """Academic year/session for a school."""

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='academic_years'
    )
    name = models.CharField(_('name'), max_length=100)  # e.g., "2024/2025"
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    is_current = models.BooleanField(_('is current'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('academic year')
        verbose_name_plural = _('academic years')
        unique_together = ['school', 'name']
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'is_current']),
        ]

    def __str__(self):
        return f'{self.school.name} - {self.name}'

    def save(self, *args, **kwargs):
        """Ensure only one current academic year per school."""
        if self.is_current:
            AcademicYear.objects.filter(
                school=self.school,
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Term(models.Model):
    """School term/semester."""

    class TermType(models.TextChoices):
        FIRST = 'first', _('First Term')
        SECOND = 'second', _('Second Term')
        THIRD = 'third', _('Third Term')

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='terms'
    )
    name = models.CharField(_('name'), max_length=100)
    term_type = models.CharField(
        _('term type'),
        max_length=20,
        choices=TermType.choices
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    is_current = models.BooleanField(_('is current'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('term')
        verbose_name_plural = _('terms')
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['academic_year', 'is_current']),
        ]

    def __str__(self):
        return f'{self.academic_year.school.name} - {self.name}'

    def save(self, *args, **kwargs):
        """Ensure only one current term per academic year."""
        if self.is_current:
            Term.objects.filter(
                academic_year=self.academic_year,
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
