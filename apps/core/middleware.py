"""
Core middleware for the application.
"""
from django.shortcuts import redirect
from django.urls import reverse
from apps.schools.models import School


class ActiveSchoolMiddleware:
    """
    Middleware to set the active school in the request.
    The active school is stored in the session.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get active school ID from session
        active_school_id = request.session.get('active_school_id')

        # Try to get the active school
        if active_school_id:
            try:
                request.active_school = School.objects.select_related(
                    'owner', 'subscription'
                ).get(id=active_school_id, is_active=True)
            except School.DoesNotExist:
                request.active_school = None
                del request.session['active_school_id']
        else:
            request.active_school = None

        # If user is authenticated and no active school, try to set one
        if (
            request.user.is_authenticated and
            not request.active_school and
            not request.path.startswith('/admin/') and
            not request.path.startswith('/accounts/') and
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/')
        ):
            # Get user's first school
            schools = request.user.get_schools()
            if schools:
                request.active_school = schools[0]
                request.session['active_school_id'] = request.active_school.id

        response = self.get_response(request)
        return response


class SchoolSwitchMiddleware:
    """
    Middleware to handle school switching via query parameter.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for school switch parameter
        school_id = request.GET.get('switch_school')

        if school_id and request.user.is_authenticated:
            try:
                # Verify user has access to this school
                school = School.objects.get(id=school_id, is_active=True)

                # Check if user has access
                user_schools = request.user.get_schools()
                if school in user_schools or request.user.role == 'super_admin':
                    request.session['active_school_id'] = school.id
            except School.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
