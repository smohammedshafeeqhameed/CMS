from django.contrib import admin
from .models import StudentProfile, Certificate, SubjectEvaluation

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_number', 'course', 'current_semester', 'cgpa', 'batch')
    list_filter = ('course', 'current_semester', 'batch', 'aiml_cert_verified', 'stem_badge_verified')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'enrollment_number')
    raw_id_fields = ('user', 'course')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'issuing_organization', 'issue_date', 'is_verified')
    list_filter = ('is_verified', 'issuing_organization')
    search_fields = ('name', 'student__username', 'issuing_organization')
    raw_id_fields = ('student',)

@admin.register(SubjectEvaluation)
class SubjectEvaluationAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'created_at')
    list_filter = ('semester', 'subject')
    search_fields = ('student__username', 'subject__name')
    raw_id_fields = ('student', 'subject', 'course')
