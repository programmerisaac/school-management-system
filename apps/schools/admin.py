"""
Schools admin.
"""
from django.contrib import admin
from .models import (
    School, SubscriptionPlan, Subscription,
    SchoolMembership, AcademicYear, Term
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'school_type', 'is_active', 'created_at']
    list_filter = ['school_type', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'yearly_price', 'max_students', 'is_active']
    list_filter = ['is_active', 'is_featured']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['plan', 'billing_cycle', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'billing_cycle']


@admin.register(SchoolMembership)
class SchoolMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']
    search_fields = ['user__email', 'school__name']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'school']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'name', 'term_type', 'start_date', 'end_date', 'is_current']
    list_filter = ['term_type', 'is_current']
