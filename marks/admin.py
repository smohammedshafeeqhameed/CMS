from django.contrib import admin
from .models import AssessmentType, InternalMark, SemesterResult

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'weightage', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']

@admin.register(InternalMark)
class InternalMarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'assessment_type', 'marks_obtained', 'max_marks', 'semester', 'academic_year']
    list_filter = ['semester', 'academic_year', 'assessment_type', 'subject']
    search_fields = ['student__username', 'subject__name']
    raw_id_fields = ['student', 'subject', 'assessment_type', 'entered_by']
    date_hierarchy = 'assessment_date'

@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'academic_year', 'sgpa', 'cgpa', 'total_credits', 'passed_subjects']
    list_filter = ['semester', 'academic_year']
    search_fields = ['student__username']
    raw_id_fields = ['student']
    readonly_fields = ['calculated_at']
