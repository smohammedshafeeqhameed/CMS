from django.db import models
from django.conf import settings

class InterviewSchedule(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    application = models.ForeignKey('placements.Application', on_delete=models.CASCADE, related_name='interviews')
    date_time = models.DateTimeField()
    location_link = models.URLField(blank=True)
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='scheduled_interviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Interview for {self.application} on {self.date_time}"
