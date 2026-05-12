from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import Department

class AnnouncementCategory(models.Model):
    """Categories for announcements"""
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Academic, Placement, Events, General, Fees, Exam")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Announcement Category"
        verbose_name_plural = "Announcement Categories"

    def __str__(self):
        return self.name


class Announcement(models.Model):
    """Announcements posted by Admin, HOD, or Faculty"""
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    TARGET_AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('STUDENTS', 'Students Only'),
        ('FACULTY', 'Faculty Only'),
        ('DEPARTMENT', 'Department Only'),
        ('COURSE', 'Course Only'),
        ('BATCH', 'Batch Only'),
        ('INDIVIDUAL', 'Individual Student Only'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Announcement content")
    target_individual = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='personal_announcements',
        help_text="Target a specific student for personalized notices"
    )
    category = models.ForeignKey(
        AnnouncementCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
        help_text="Category of announcement"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Priority level"
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_announcements',
        limit_choices_to={'role__in': ['SUPER_ADMIN', 'ADMIN', 'HOD', 'FACULTY']}
    )
    posted_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Announcement expiry date (optional)"
    )
    
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        default='ALL',
        help_text="Target audience for this announcement"
    )
    target_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
        help_text="Target department (if applicable)"
    )
    target_batch = models.CharField(
        max_length=50,
        blank=True,
        help_text="Target batch (e.g., 2024-2028)"
    )
    
    attachment = models.FileField(
        upload_to='announcements/',
        blank=True,
        null=True,
        help_text="Optional attachment file"
    )
    is_active = models.BooleanField(default=True, help_text="Whether announcement is active")
    is_pinned = models.BooleanField(default=False, help_text="Pin announcement to top")

    class Meta:
        ordering = ['-is_pinned', '-posted_at']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        indexes = [
            models.Index(fields=['target_audience', 'is_active']),
            models.Index(fields=['posted_at']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_target_audience_display()}"
    
    def is_expired(self):
        """Check if announcement has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def is_visible_to_user(self, user):
        """Check if announcement is visible to a specific user"""
        if not self.is_active or self.is_expired():
            return False
        
        if self.target_audience == 'ALL':
            return True
        elif self.target_audience == 'STUDENTS' and user.is_student:
            return True
        elif self.target_audience == 'FACULTY' and user.is_faculty:
            return True
        elif self.target_audience == 'DEPARTMENT':
            if self.target_department and user.department_fk == self.target_department:
                return True
        elif self.target_audience == 'BATCH':
            if user.is_student and hasattr(user, 'student_profile'):
                if user.student_profile.batch == self.target_batch:
                    return True
        elif self.target_audience == 'INDIVIDUAL':
            if self.target_individual == user:
                return True
        
        return False


class AnnouncementRead(models.Model):
    """Track which users have read which announcements"""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='read_announcements'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-read_at']
        verbose_name = "Announcement Read"
        verbose_name_plural = "Announcement Reads"
        unique_together = [['announcement', 'user']]
        indexes = [
            models.Index(fields=['announcement', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"


class Event(models.Model):
    """College events"""
    TARGET_AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('STUDENTS', 'Students Only'),
        ('FACULTY', 'Faculty Only'),
        ('DEPARTMENT', 'Department Only'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField(help_text="Event date and time")
    venue = models.CharField(max_length=200, help_text="Event venue/location")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        limit_choices_to={'role__in': ['SUPER_ADMIN', 'ADMIN', 'HOD', 'FACULTY']}
    )
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        default='ALL'
    )
    target_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    registration_required = models.BooleanField(
        default=False,
        help_text="Whether registration is required"
    )
    max_participants = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['event_date']
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=['event_date', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%Y-%m-%d')}"
    
    def get_registered_count(self):
        """Get number of registered participants"""
        return self.registrations.count()
    
    def is_registration_full(self):
        """Check if registration is full"""
        if self.max_participants:
            return self.get_registered_count() >= self.max_participants
        return False


class EventRegistration(models.Model):
    """Event registrations by students"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        limit_choices_to={'role': 'STUDENT'}
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False, help_text="Whether student attended the event")
    attendance_marked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-registered_at']
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
        unique_together = [['event', 'student']]
        indexes = [
            models.Index(fields=['event', 'student']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.event.title}"
