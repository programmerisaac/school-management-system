"""
Celery tasks for student management.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def generate_attendance_reports():
    """Generate weekly attendance reports."""
    from .models import Student, Attendance
    from apps.communications.models import EmailLog

    # Get date range for last week
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)

    students = Student.objects.filter(status='active').select_related('school')

    report_count = 0
    for student in students:
        # Calculate attendance for the week
        attendance_records = Attendance.objects.filter(
            student=student,
            date__gte=week_ago,
            date__lte=today
        )

        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()

        if total_days > 0:
            attendance_rate = (present_days / total_days) * 100

            # Generate report
            report = f"""
Weekly Attendance Report for {student.get_full_name()}
Week: {week_ago.strftime('%d %B %Y')} - {today.strftime('%d %B %Y')}

Total Days: {total_days}
Present: {present_days}
Absent: {absent_days}
Late: {late_days}
Attendance Rate: {attendance_rate:.2f}%

School: {student.school.name}
"""

            # Send to primary guardian
            guardians = student.student_guardians.filter(is_primary=True).select_related('guardian')

            for sg in guardians:
                guardian = sg.guardian

                try:
                    send_mail(
                        subject=f'Weekly Attendance Report - {student.get_full_name()}',
                        message=report,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[guardian.email],
                        fail_silently=False,
                    )

                    EmailLog.objects.create(
                        school=student.school,
                        recipient_email=guardian.email,
                        recipient_name=guardian.get_full_name(),
                        subject=f'Weekly Attendance Report',
                        body=report,
                        status='sent',
                        sent_at=timezone.now()
                    )

                    report_count += 1
                except Exception as e:
                    EmailLog.objects.create(
                        school=student.school,
                        recipient_email=guardian.email,
                        recipient_name=guardian.get_full_name(),
                        subject=f'Weekly Attendance Report',
                        body=report,
                        status='failed',
                        error_message=str(e)
                    )

    return f'Generated {report_count} attendance reports'


@shared_task
def send_absence_alerts():
    """Send alerts for student absences."""
    from .models import Attendance
    from apps.communications.models import EmailLog, Notification

    # Get today's absences
    today = timezone.now().date()
    absences = Attendance.objects.filter(
        date=today,
        status='absent'
    ).select_related('student', 'student__school')

    count = 0
    for attendance in absences:
        student = attendance.student

        # Send notification to parent
        guardians = student.student_guardians.filter(is_primary=True).select_related('guardian')

        for sg in guardians:
            guardian = sg.guardian

            message = f"""
Dear {guardian.get_full_name()},

This is to inform you that {student.get_full_name()} was marked absent on {today.strftime('%d %B %Y')}.

If this is unexpected, please contact the school immediately.

{student.school.name}
"""

            try:
                send_mail(
                    subject=f'Absence Alert - {student.get_full_name()}',
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[guardian.email],
                    fail_silently=False,
                )

                EmailLog.objects.create(
                    school=student.school,
                    recipient_email=guardian.email,
                    recipient_name=guardian.get_full_name(),
                    subject='Absence Alert',
                    body=message,
                    status='sent',
                    sent_at=timezone.now()
                )

                count += 1
            except Exception:
                pass

    return f'Sent {count} absence alerts'
