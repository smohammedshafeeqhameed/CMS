from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    
    # Personal Details
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    batch = models.CharField(max_length=50, blank=True, help_text="e.g. Class of 2024")
    bio = models.TextField(max_length=500, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    # Academic Details (New Fields)
    enrollment_number = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Unique enrollment number")
    admission_date = models.DateField(blank=True, null=True, help_text="Date of admission")
    current_semester = models.IntegerField(default=1, help_text="Current semester (1-8 for UG, 1-4 for PG)")
    academic_year = models.CharField(max_length=20, blank=True, help_text="e.g. 2024-2025")
    course = models.ForeignKey('academics.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profiles')
    
    # Contact & Personal Info
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, help_text="e.g. A+, B-, O+")
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions (optional, privacy-controlled)")
    
    # Social Links
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn Profile")
    github_url = models.URLField(blank=True, verbose_name="GitHub Profile")

    # Skills & Badges
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    
    # Verification
    stem_badge = models.FileField(upload_to='badges/', blank=True, null=True)
    stem_badge_verified = models.BooleanField(default=False)
    
    aiml_cert = models.FileField(upload_to='certificates/', blank=True, null=True)
    aiml_cert_verified = models.BooleanField(default=False)
    
    employability_score = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"
    
    def get_profile_completeness(self):
        """Calculate profile completeness percentage"""
        fields = [
            self.profile_photo, self.bio, self.cgpa, self.enrollment_number,
            self.admission_date, self.resume, self.linkedin_url, self.skills,
            self.guardian_name, self.guardian_contact, self.address
        ]
        completed = sum(1 for field in fields if field)
        total = len(fields)
        return int((completed / total) * 100) if total > 0 else 0


class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    certificate_file = models.FileField(upload_to='certificates/')
    
    # Verification & Badging
    is_verified = models.BooleanField(default=False)
    skill_badge = models.ImageField(upload_to='badges/', blank=True, null=True, help_text="Badge awarded upon verification")
    
    def __str__(self):
        return f"{self.name} - {self.student.username}"


class SubjectEvaluation(models.Model):
    """Model to store AI-based subject evaluation results for students"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='evaluations')
    course = models.ForeignKey('academics.Course', on_delete=models.CASCADE, related_name='evaluations')
    semester = models.IntegerField()
    
    # Results
    score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage score")
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    
    # AI Insights
    ai_feedback = models.TextField(help_text="Suggestions and tips based on performance")
    ai_recommendations = models.TextField(help_text="Specific learning resources or topics to focus on")
    
    # raw test data (optional, for review)
    test_details = models.JSONField(default=dict, blank=True, help_text="Question-wise student response data")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Subject Evaluation"
        verbose_name_plural = "Subject Evaluations"

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.code} ({self.score}%)"
