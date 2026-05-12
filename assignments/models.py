from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import Subject

class Assignment(models.Model):
    """Assignment model for faculty to create assignments"""
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Assignment description and requirements")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_assignments',
        limit_choices_to={'role': 'FACULTY'}
    )
    due_date = models.DateTimeField(help_text="Assignment deadline")
    max_marks = models.IntegerField(default=100, help_text="Maximum marks for this assignment")
    attachment = models.FileField(
        upload_to='assignments/',
        blank=True,
        null=True,
        help_text="Assignment file (PDF, DOC, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether assignment is active")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        indexes = [
            models.Index(fields=['subject', 'faculty']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    def is_overdue(self):
        """Check if assignment is past due date"""
        return timezone.now() > self.due_date
    
    def get_submission_count(self):
        """Get number of submissions"""
        return self.submissions.count()
    
    def get_pending_submissions_count(self):
        """Get number of pending submissions (not graded)"""
        return self.submissions.filter(marks_obtained__isnull=True).count()


class AssignmentSubmission(models.Model):
    """Student assignment submissions"""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        limit_choices_to={'role': 'STUDENT'}
    )
    submission_file = models.FileField(
        upload_to='submissions/',
        help_text="Submitted assignment file"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(null=True, blank=True, help_text="Marks awarded")
    feedback = models.TextField(blank=True, help_text="Faculty feedback")
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        limit_choices_to={'role': 'FACULTY'}
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False, help_text="Whether submission was late")
    remarks = models.TextField(blank=True, help_text="Additional remarks")

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"
        unique_together = [['assignment', 'student']]
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        # Check if submission is late
        if not self.pk:  # New submission
            if timezone.now() > self.assignment.due_date:
                self.is_late = True
        super().save(*args, **kwargs)
    
    def get_percentage(self):
        """Calculate percentage marks"""
        if self.marks_obtained is not None and self.assignment.max_marks > 0:
            return (self.marks_obtained / self.assignment.max_marks) * 100
        return None
