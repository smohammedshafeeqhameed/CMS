from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from academics.models import Subject

class AssessmentType(models.Model):
    """Types of assessments (Quiz, Midterm, Assignment, Project, etc.)"""
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Quiz, Midterm, Assignment, Project")
    weightage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weightage percentage in final marks"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Assessment Type"
        verbose_name_plural = "Assessment Types"

    def __str__(self):
        return f"{self.name} ({self.weightage}%)"


class InternalMark(models.Model):
    """Internal marks for students"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='internal_marks',
        limit_choices_to={'role': 'STUDENT'}
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='internal_marks')
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Marks obtained by student"
    )
    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Maximum marks for this assessment"
    )
    assessment_date = models.DateField(help_text="Date of assessment")
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entered_marks',
        limit_choices_to={'role': 'FACULTY'}
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester number"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assessment_date', 'student']
        verbose_name = "Internal Mark"
        verbose_name_plural = "Internal Marks"
        unique_together = [['student', 'subject', 'assessment_type', 'semester', 'academic_year']]
        indexes = [
            models.Index(fields=['student', 'subject', 'semester']),
            models.Index(fields=['subject', 'assessment_type']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.assessment_type.name} ({self.marks_obtained}/{self.max_marks})"
    
    def get_percentage(self):
        """Calculate percentage marks"""
        if self.max_marks > 0:
            return (self.marks_obtained / self.max_marks) * 100
        return 0
    
    def get_weighted_marks(self):
        """Calculate weighted marks based on assessment type weightage"""
        percentage = self.get_percentage()
        return (percentage * self.assessment_type.weightage) / 100


class SemesterResult(models.Model):
    """Semester-wise results and GPA calculation"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='semester_results',
        limit_choices_to={'role': 'STUDENT'}
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester number"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    
    sgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Semester Grade Point Average"
    )
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Cumulative Grade Point Average"
    )
    total_credits = models.IntegerField(default=0, help_text="Total credits in semester")
    earned_credits = models.IntegerField(default=0, help_text="Credits earned")
    passed_subjects = models.IntegerField(default=0)
    failed_subjects = models.IntegerField(default=0)
    
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-academic_year', '-semester', 'student']
        verbose_name = "Semester Result"
        verbose_name_plural = "Semester Results"
        unique_together = [['student', 'semester', 'academic_year']]
        indexes = [
            models.Index(fields=['student', 'semester']),
        ]

    def __str__(self):
        return f"{self.student.username} - Sem {self.semester} (SGPA: {self.sgpa}, CGPA: {self.cgpa})"
