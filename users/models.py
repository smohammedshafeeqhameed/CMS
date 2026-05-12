from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('HOD', 'Head of Department'),
        ('FACULTY', 'Faculty Mentor'),
        ('STUDENT', 'Student'),
        ('PLACEMENT_CELL', 'Placement Cell'),
        ('PLACEMENT_OFFICER', 'Placement Officer'),
        ('INDUSTRY', 'Industry Supervisor'),
        ('EMPLOYER', 'Employer'),
        ('LIBRARIAN', 'Librarian'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    department = models.CharField(max_length=100, blank=True, help_text="Department for Students/Faculty")
    department_fk = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="Department (Foreign Key)"
    )
    phone_number = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True, help_text="Employee ID for staff")
    designation = models.CharField(max_length=100, blank=True, help_text="Designation/Rank")
    is_approved = models.BooleanField(default=False, help_text="Whether user account is approved by admin")
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users',
        limit_choices_to={'role__in': ['SUPER_ADMIN', 'ADMIN']}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Overall attendance percentage")
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, help_text="Total marks obtained")
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00, help_text="Overall GPA")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == 'STUDENT'
    
    @property
    def is_placement_cell(self):
        return self.role == 'PLACEMENT_CELL'

    @property
    def is_faculty(self):
        return self.role == 'FACULTY'

    @property
    def is_industry(self):
        return self.role == 'INDUSTRY'

    @property
    def is_employer(self):
        return self.role == 'EMPLOYER'
    
    @property
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_hod(self):
        return self.role == 'HOD'
    
    @property
    def is_placement_officer(self):
        return self.role == 'PLACEMENT_OFFICER'
    
    @property
    def is_librarian(self):
        return self.role == 'LIBRARIAN'
    
    def can_approve_users(self):
        """Check if user can approve other users"""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'HOD']
    
    def can_manage_departments(self):
        """Check if user can manage departments"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']


class FacultyProfile(models.Model):
    """Extended profile for Faculty members"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=50, unique=True, help_text="Unique employee ID")
    qualification = models.TextField(help_text="Educational qualifications")
    specialization = models.CharField(max_length=200, help_text="Area of specialization")
    years_of_experience = models.IntegerField(default=0, help_text="Years of teaching experience")
    office_location = models.CharField(max_length=100, blank=True, help_text="Office room number/location")
    office_hours = models.CharField(max_length=100, blank=True, help_text="e.g. Mon-Fri 10AM-12PM")
    profile_photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Social Links
    linkedin_url = models.URLField(blank=True)
    research_gate_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Faculty Profile"
        verbose_name_plural = "Faculty Profiles"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"Faculty Profile: {self.user.get_full_name() or self.user.username}"
    
    def get_profile_completeness(self):
        """Calculate profile completeness percentage"""
        fields = [
            self.profile_photo, self.bio, self.qualification, self.specialization,
            self.office_location, self.office_hours, self.linkedin_url
        ]
        completed = sum(1 for field in fields if field)
        total = len(fields)
        return int((completed / total) * 100) if total > 0 else 0
