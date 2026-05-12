from django.db import models
from django.conf import settings

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField()
    department = models.CharField(max_length=100, blank=True)
    competencies = models.CharField(max_length=500, help_text="Comma-separated tags")
    stipend_range = models.CharField(max_length=100)
    eligibility_criteria = models.TextField(blank=True, help_text="Qualification, CGPA, backlogs etc.")
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_competencies_list(self):
        return [c.strip() for c in self.competencies.split(',')] if self.competencies else []

class Application(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SCREENING', 'In Screening'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    faculty_approved = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')
    
    def __str__(self):
        return f"{self.student.username} -> {self.job.title}"
