from django.contrib import admin
from .models import Assignment, AssignmentSubmission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'faculty', 'due_date', 'max_marks', 'is_active', 'created_at']
    list_filter = ['is_active', 'subject', 'due_date', 'created_at']
    search_fields = ['title', 'subject__name', 'faculty__username']
    raw_id_fields = ['subject', 'faculty']
    date_hierarchy = 'due_date'

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at', 'is_late', 'marks_obtained', 'graded_by']
    list_filter = ['is_late', 'submitted_at', 'assignment__subject']
    search_fields = ['student__username', 'assignment__title']
    raw_id_fields = ['assignment', 'student', 'graded_by']
    readonly_fields = ['submitted_at']
