"""
Student utilities.
"""
from django.utils import timezone


def get_student_attendance_summary(student, start_date=None, end_date=None):
    """
    Get attendance summary for a student.

    Args:
        student: Student object
        start_date: Start date (default: current term start)
        end_date: End date (default: today)

    Returns:
        dict: Attendance summary
    """
    from .models import Attendance

    if end_date is None:
        end_date = timezone.now().date()

    if start_date is None:
        # Get current term start date
        current_term = student.school.academic_years.filter(
            is_current=True
        ).first().terms.filter(is_current=True).first()

        if current_term:
            start_date = current_term.start_date
        else:
            start_date = end_date - timezone.timedelta(days=30)

    attendance = Attendance.objects.filter(
        student=student,
        date__gte=start_date,
        date__lte=end_date
    )

    total = attendance.count()
    present = attendance.filter(status='present').count()
    absent = attendance.filter(status='absent').count()
    late = attendance.filter(status='late').count()
    excused = attendance.filter(status='excused').count()

    attendance_rate = (present / total * 100) if total > 0 else 0

    return {
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'excused': excused,
        'attendance_rate': round(attendance_rate, 2),
    }


def get_student_grade_summary(student, term=None):
    """
    Get grade summary for a student.

    Args:
        student: Student object
        term: Term object (default: current term)

    Returns:
        dict: Grade summary
    """
    from apps.academics.models import Grade

    if term is None:
        # Get current term
        term = student.school.academic_years.filter(
            is_current=True
        ).first().terms.filter(is_current=True).first()

    grades = Grade.objects.filter(
        student=student,
        exam_subject__exam__term=term
    ).select_related('exam_subject__subject')

    total_subjects = grades.count()
    total_marks = sum(g.marks_obtained for g in grades)
    total_possible = sum(g.exam_subject.total_marks for g in grades)

    average = (total_marks / total_possible * 100) if total_possible > 0 else 0

    # Count grade distribution
    grade_distribution = {}
    for g in grades:
        grade_distribution[g.grade] = grade_distribution.get(g.grade, 0) + 1

    return {
        'total_subjects': total_subjects,
        'total_marks': total_marks,
        'total_possible': total_possible,
        'average': round(average, 2),
        'grade_distribution': grade_distribution,
    }


def promote_students(from_class, to_class):
    """
    Promote students from one class to another.

    Args:
        from_class: Class object (source)
        to_class: Class object (destination)

    Returns:
        int: Number of students promoted
    """
    from .models import Student

    students = Student.objects.filter(current_class=from_class, status='active')
    count = students.update(current_class=to_class)

    return count
