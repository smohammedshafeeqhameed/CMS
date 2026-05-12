from django.contrib import admin
from .models import InterviewSchedule

@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ('application', 'date_time', 'interviewer', 'status')
    list_filter = ('status', 'date_time')
    search_fields = ('application__student__username', 'interviewer__username', 'feedback')
    raw_id_fields = ('application', 'interviewer')
