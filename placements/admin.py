from django.contrib import admin
from .models import JobPosting, Application

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'department', 'deadline', 'is_active')
    list_filter = ('is_active', 'company', 'deadline')
    search_fields = ('title', 'company', 'description', 'competencies')
    raw_id_fields = ('posted_by',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'faculty_approved', 'applied_at')
    list_filter = ('status', 'faculty_approved', 'applied_at')
    search_fields = ('student__username', 'job__title', 'job__company')
    raw_id_fields = ('student', 'job')
    list_editable = ('status', 'faculty_approved')
