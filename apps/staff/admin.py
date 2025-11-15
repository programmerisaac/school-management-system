"""
Staff admin.
"""
from django.contrib import admin
from .models import StaffMember, StaffAttendance, Leave


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'designation', 'staff_type', 'status', 'joining_date']
    list_filter = ['staff_type', 'employment_type', 'status']
    search_fields = ['employee_id', 'user__email', 'designation']


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'check_in_time', 'check_out_time']
    list_filter = ['status', 'date']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
