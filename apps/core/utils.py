"""
Core utility functions.
"""
import random
import string
from django.utils.text import slugify


def generate_unique_code(length=8):
    """Generate a unique random code."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_admission_number(school_code, year=None):
    """
    Generate admission number for students.

    Format: SCHOOL-YEAR-XXXX
    Example: ABC-2024-0001
    """
    from datetime import datetime

    if year is None:
        year = datetime.now().year

    # Get the last admission number for this school and year
    from apps.students.models import Student

    last_student = Student.objects.filter(
        admission_number__startswith=f'{school_code}-{year}'
    ).order_by('-admission_number').first()

    if last_student:
        # Extract the sequential number and increment
        last_seq = int(last_student.admission_number.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f'{school_code}-{year}-{new_seq:04d}'


def generate_employee_id(school_code):
    """
    Generate employee ID for staff.

    Format: SCHOOL-EMP-XXXX
    Example: ABC-EMP-0001
    """
    from apps.staff.models import StaffMember

    last_staff = StaffMember.objects.filter(
        employee_id__startswith=f'{school_code}-EMP'
    ).order_by('-employee_id').first()

    if last_staff:
        last_seq = int(last_staff.employee_id.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f'{school_code}-EMP-{new_seq:04d}'


def get_academic_year_name(start_date, end_date):
    """
    Generate academic year name from dates.

    Example: 2024/2025
    """
    return f'{start_date.year}/{end_date.year}'


def calculate_age(date_of_birth):
    """Calculate age from date of birth."""
    from datetime import date

    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def generate_unique_slug(model_class, text, field_name='slug'):
    """
    Generate a unique slug for a model.

    Args:
        model_class: The model class
        text: Text to slugify
        field_name: Name of the slug field

    Returns:
        str: Unique slug
    """
    slug = slugify(text)
    unique_slug = slug
    counter = 1

    while model_class.objects.filter(**{field_name: unique_slug}).exists():
        unique_slug = f'{slug}-{counter}'
        counter += 1

    return unique_slug


def format_currency(amount, currency_symbol='₦'):
    """Format amount as currency."""
    return f'{currency_symbol}{amount:,.2f}'


def get_term_name(term_number):
    """Get term name from number."""
    terms = {
        1: 'First Term',
        2: 'Second Term',
        3: 'Third Term',
    }
    return terms.get(term_number, f'Term {term_number}')


def calculate_gpa(grades):
    """
    Calculate GPA from list of grades.

    Args:
        grades: List of Grade objects

    Returns:
        float: GPA (0-4.0 scale)
    """
    if not grades:
        return 0.0

    grade_points = {
        'A+': 4.0,
        'A': 4.0,
        'B+': 3.5,
        'B': 3.0,
        'C': 2.0,
        'D': 1.0,
        'F': 0.0,
    }

    total_points = sum(grade_points.get(g.grade, 0) for g in grades)
    return round(total_points / len(grades), 2)


def send_notification(user, title, message, notification_type='info', link=''):
    """
    Send in-app notification to user.

    Args:
        user: User object
        title: Notification title
        message: Notification message
        notification_type: Type of notification (info, success, warning, error)
        link: Optional link
    """
    from apps.communications.models import Notification

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )


def bulk_send_notification(users, title, message, notification_type='info', link=''):
    """
    Send notification to multiple users.

    Args:
        users: QuerySet or list of User objects
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        link: Optional link
    """
    from apps.communications.models import Notification

    notifications = [
        Notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
        for user in users
    ]

    Notification.objects.bulk_create(notifications)


def get_percentage(value, total):
    """Calculate percentage."""
    if total == 0:
        return 0
    return round((value / total) * 100, 2)


def truncate_text(text, length=100, suffix='...'):
    """Truncate text to specified length."""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix
