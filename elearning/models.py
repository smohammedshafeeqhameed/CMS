from django.db import models
from django.conf import settings
from academics.models import Subject

class MaterialCategory(models.Model):
    """Categories for learning materials"""
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Lecture Notes, Videos, Books, Lab Manuals")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Material Category"
        verbose_name_plural = "Material Categories"

    def __str__(self):
        return self.name


class LearningMaterial(models.Model):
    """E-learning materials uploaded by faculty"""
    ACCESS_LEVEL_CHOICES = [
        ('PUBLIC', 'Public - All Students'),
        ('DEPARTMENT', 'Department Only'),
        ('COURSE', 'Course Only'),
        ('SUBJECT', 'Subject Only'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Description of the material")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='learning_materials',
        help_text="Subject this material belongs to"
    )
    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        help_text="Category of material"
    )
    file = models.FileField(
        upload_to='learning_materials/',
        help_text="Upload PDF, DOC, PPT, Video, or other learning material"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_materials',
        limit_choices_to={'role': 'FACULTY'}
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_public = models.BooleanField(
        default=False,
        help_text="Make material visible to all students"
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='SUBJECT',
        help_text="Access level for this material"
    )
    download_count = models.IntegerField(default=0, help_text="Number of times downloaded")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Learning Material"
        verbose_name_plural = "Learning Materials"
        indexes = [
            models.Index(fields=['subject', 'is_active']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class MaterialAccess(models.Model):
    """Track student access to learning materials"""
    material = models.ForeignKey(
        LearningMaterial,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='material_accesses',
        limit_choices_to={'role': 'STUDENT'}
    )
    accessed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(
        max_length=20,
        choices=[('VIEW', 'Viewed'), ('DOWNLOAD', 'Downloaded')],
        default='VIEW'
    )

    class Meta:
        ordering = ['-accessed_at']
        verbose_name = "Material Access"
        verbose_name_plural = "Material Accesses"
        indexes = [
            models.Index(fields=['material', 'student']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.material.title} - {self.action}"
