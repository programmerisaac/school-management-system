"""
Academic models including classes, subjects, exams, and grading.
"""
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _
import shortuuid


class Class(models.Model):
    """Class/Grade model."""

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='classes'
    )
    name = models.CharField(_('class name'), max_length=100)  # e.g., "Grade 1", "JSS 1"
    section = models.CharField(_('section'), max_length=50, blank=True)  # e.g., "A", "B"
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='classes'
    )
    class_teacher = models.ForeignKey(
        'staff.StaffMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_classes',
        limit_choices_to={'staff_type': 'teaching'}
    )
    room_number = models.CharField(_('room number'), max_length=50, blank=True)
    capacity = models.IntegerField(_('capacity'), default=30)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('class')
        verbose_name_plural = _('classes')
        unique_together = ['school', 'name', 'section', 'academic_year']
        ordering = ['name', 'section']
        indexes = [
            models.Index(fields=['school', 'academic_year']),
        ]

    def __str__(self):
        if self.section:
            return f'{self.name} - {self.section}'
        return self.name

    def get_student_count(self):
        """Get number of students in this class (cached)."""
        cache_key = f'class_student_count_{self.id}'
        count = cache.get(cache_key)

        if count is None:
            count = self.students.filter(status='active').count()
            cache.set(cache_key, count, 600)  # Cache for 10 minutes

        return count


class Subject(models.Model):
    """Subject model."""

    class SubjectType(models.TextChoices):
        CORE = 'core', _('Core Subject')
        ELECTIVE = 'elective', _('Elective Subject')
        EXTRA = 'extra', _('Extra Curricular')

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    name = models.CharField(_('subject name'), max_length=200)
    code = models.CharField(_('subject code'), max_length=20)
    subject_type = models.CharField(
        _('subject type'),
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.CORE
    )
    description = models.TextField(_('description'), blank=True)
    pass_mark = models.IntegerField(_('pass mark'), default=40)
    total_mark = models.IntegerField(_('total mark'), default=100)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        unique_together = ['school', 'code']
        ordering = ['name']
        indexes = [
            models.Index(fields=['school', 'subject_type']),
        ]

    def __str__(self):
        return f'{self.name} ({self.code})'


class ClassSubject(models.Model):
    """Subjects assigned to classes."""

    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='class_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_classes'
    )
    teacher = models.ForeignKey(
        'staff.StaffMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_assignments',
        limit_choices_to={'staff_type': 'teaching'}
    )

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('class subject')
        verbose_name_plural = _('class subjects')
        unique_together = ['class_obj', 'subject']

    def __str__(self):
        return f'{self.class_obj} - {self.subject}'


class Exam(models.Model):
    """Exam model."""

    class ExamType(models.TextChoices):
        MIDTERM = 'midterm', _('Mid-term')
        FINAL = 'final', _('Final Exam')
        QUIZ = 'quiz', _('Quiz')
        ASSIGNMENT = 'assignment', _('Assignment')
        TEST = 'test', _('Test')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    name = models.CharField(_('exam name'), max_length=200)
    exam_type = models.CharField(
        _('exam type'),
        max_length=20,
        choices=ExamType.choices
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    description = models.TextField(_('description'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('exam')
        verbose_name_plural = _('exams')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['school', 'term']),
            models.Index(fields=['-start_date']),
        ]

    def __str__(self):
        return f'{self.name} - {self.term}'


class ExamSubject(models.Model):
    """Subjects for specific exams."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='exam_subjects'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_exams'
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='class_exams'
    )
    exam_date = models.DateField(_('exam date'))
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))
    total_marks = models.IntegerField(_('total marks'), default=100)
    pass_marks = models.IntegerField(_('pass marks'), default=40)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('exam subject')
        verbose_name_plural = _('exam subjects')
        unique_together = ['exam', 'subject', 'class_obj']
        ordering = ['exam_date', 'start_time']

    def __str__(self):
        return f'{self.exam} - {self.subject} ({self.class_obj})'


class Grade(models.Model):
    """Student grades/marks."""

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    exam_subject = models.ForeignKey(
        ExamSubject,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    marks_obtained = models.DecimalField(
        _('marks obtained'),
        max_digits=5,
        decimal_places=2
    )
    grade = models.CharField(_('grade'), max_length=2, blank=True)  # A, B, C, etc.
    remarks = models.TextField(_('remarks'), blank=True)
    is_absent = models.BooleanField(_('is absent'), default=False)

    # Graded by
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_exams'
    )

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('grade')
        verbose_name_plural = _('grades')
        unique_together = ['student', 'exam_subject']
        indexes = [
            models.Index(fields=['student', 'exam_subject']),
            models.Index(fields=['exam_subject']),
        ]

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.exam_subject.subject} ({self.marks_obtained})'

    def calculate_grade(self):
        """Calculate letter grade based on percentage."""
        percentage = (self.marks_obtained / self.exam_subject.total_marks) * 100

        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'

    def save(self, *args, **kwargs):
        """Auto-calculate grade."""
        if not self.is_absent:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)


class Assignment(models.Model):
    """Assignment/homework model."""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        CLOSED = 'closed', _('Closed')

    id = models.CharField(
        max_length=22,
        primary_key=True,
        default=shortuuid.uuid,
        editable=False
    )
    class_subject = models.ForeignKey(
        ClassSubject,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    due_date = models.DateTimeField(_('due date'))
    total_marks = models.IntegerField(_('total marks'), default=100)
    attachment = models.FileField(
        _('attachment'),
        upload_to='assignments/',
        blank=True,
        null=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assignments'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('assignment')
        verbose_name_plural = _('assignments')
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.title} - {self.class_subject}'


class AssignmentSubmission(models.Model):
    """Student assignment submissions."""

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    submission_file = models.FileField(
        _('submission file'),
        upload_to='submissions/'
    )
    submission_text = models.TextField(_('submission text'), blank=True)
    marks_obtained = models.DecimalField(
        _('marks obtained'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )
    feedback = models.TextField(_('feedback'), blank=True)
    is_late = models.BooleanField(_('is late submission'), default=False)

    submitted_at = models.DateTimeField(_('submitted at'), auto_now_add=True)
    graded_at = models.DateTimeField(_('graded at'), blank=True, null=True)

    class Meta:
        verbose_name = _('assignment submission')
        verbose_name_plural = _('assignment submissions')
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.assignment.title}'

    def save(self, *args, **kwargs):
        """Check if submission is late."""
        if self.submitted_at and self.assignment.due_date:
            self.is_late = self.submitted_at > self.assignment.due_date
        super().save(*args, **kwargs)
