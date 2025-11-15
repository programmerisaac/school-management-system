"""
Custom decorators for views.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def school_required(view_func):
    """
    Decorator to ensure user has an active school selected.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'active_school') or request.active_school is None:
            messages.warning(request, 'Please select a school to continue.')
            return redirect(reverse('schools:select'))
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Decorator to ensure user has one of the specified roles.
    Usage: @role_required('school_owner', 'school_admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('account_login'))

            if request.user.role not in roles and request.user.role != 'super_admin':
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(reverse('core:dashboard'))

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def subscription_required(view_func):
    """
    Decorator to ensure school has an active subscription.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'active_school') or request.active_school is None:
            messages.warning(request, 'Please select a school to continue.')
            return redirect(reverse('schools:select'))

        subscription_status = request.active_school.get_subscription_status()

        if subscription_status not in ['active', 'trial']:
            messages.error(
                request,
                'Your school subscription has expired. Please renew to continue.'
            )
            return redirect(reverse('schools:subscription'))

        return view_func(request, *args, **kwargs)
    return wrapper
