from django.contrib import admin
from .models import Department, Course, Subject, Enrollment, TimeSlot, Timetable, AcademicAdvisor

@admin.register(AcademicAdvisor)
class AcademicAdvisorAdmin(admin.ModelAdmin):
    list_display = ['faculty', 'course', 'semester', 'academic_year', 'section', 'is_active']
    list_filter = ['academic_year', 'semester', 'course', 'is_active']
    search_fields = ['faculty__username', 'faculty__email', 'course__name', 'course__code']
    list_editable = ['is_active']
    raw_id_fields = ['faculty', 'department', 'course']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'hod', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    # raw_id_fields = ['hod']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'duration_years', 'is_active']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    # raw_id_fields = ['department']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course', 'semester', 'credits', 'faculty', 'is_active']
    list_filter = ['is_active', 'course', 'semester', 'department']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    raw_id_fields = ['faculty'] # course and department are now dropdowns


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'batch', 'current_semester', 'academic_year', 'is_active']
    list_filter = ['is_active', 'course', 'academic_year', 'enrollment_date']
    search_fields = ['student__username', 'student__email', 'course__name', 'batch']
    list_editable = ['is_active', 'current_semester']
    raw_id_fields = ['student', 'course']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week']
    ordering = ['day_of_week', 'start_time']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['subject', 'time_slot', 'room', 'faculty', 'batch', 'semester', 'academic_year', 'is_active']
    list_filter = ['is_active', 'academic_year', 'semester', 'time_slot__day_of_week']
    search_fields = ['subject__name', 'room', 'batch']
    list_editable = ['is_active']
    raw_id_fields = ['subject', 'time_slot', 'faculty']
