"""
Students admin.
"""
from django.contrib import admin
from .models import Student, Guardian, StudentGuardian, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'first_name', 'last_name', 'current_class', 'status', 'admission_date']
    list_filter = ['status', 'current_class', 'gender', 'admission_date']
    search_fields = ['admission_number', 'first_name', 'last_name', 'email']


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'relationship', 'email', 'phone_number']
    list_filter = ['relationship', 'school']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(StudentGuardian)
class StudentGuardianAdmin(admin.ModelAdmin):
    list_display = ['student', 'guardian', 'is_primary', 'can_pickup']
    list_filter = ['is_primary', 'can_pickup']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'recorded_by']
    list_filter = ['status', 'date']
    search_fields = ['student__admission_number', 'student__first_name', 'student__last_name']
