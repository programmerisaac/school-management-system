"""
Redis caching utilities.
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def make_cache_key(*args, **kwargs):
    """
    Generate a cache key from arguments.
    """
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_queryset(timeout=300, key_prefix='qs'):
    """
    Decorator to cache queryset results.
    Usage: @cached_queryset(timeout=600, key_prefix='students')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f'{key_prefix}_{make_cache_key(*args, **kwargs)}'
            result = cache.get(cache_key)

            if result is None:
                result = func(*args, **kwargs)
                # Convert queryset to list for caching
                if hasattr(result, 'all'):
                    result = list(result)
                cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    Note: This requires django-redis backend.
    """
    from django_redis import get_redis_connection
    conn = get_redis_connection("default")
    keys = conn.keys(f'*{pattern}*')
    if keys:
        conn.delete(*keys)


class CacheManager:
    """Helper class for managing cache operations."""

    @staticmethod
    def get_or_set(key, callable_func, timeout=300):
        """Get from cache or set if not exists."""
        result = cache.get(key)
        if result is None:
            result = callable_func()
            cache.set(key, result, timeout)
        return result

    @staticmethod
    def invalidate_keys(*keys):
        """Invalidate multiple cache keys."""
        cache.delete_many(keys)

    @staticmethod
    def get_school_stats(school_id):
        """Get school statistics (cached)."""
        cache_key = f'school_stats_{school_id}'
        return CacheManager.get_or_set(
            cache_key,
            lambda: CacheManager._calculate_school_stats(school_id),
            timeout=600
        )

    @staticmethod
    def _calculate_school_stats(school_id):
        """Calculate school statistics."""
        from apps.students.models import Student
        from apps.staff.models import StaffMember

        stats = {
            'total_students': Student.objects.filter(
                school_id=school_id,
                status='active'
            ).count(),
            'total_staff': StaffMember.objects.filter(
                school_id=school_id,
                status='active'
            ).count(),
        }
        return stats
