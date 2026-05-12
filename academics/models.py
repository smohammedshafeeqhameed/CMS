from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    """Department model for organizing academic departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Department code (e.g., CS, EE, ME)")
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='departments_headed',
        limit_choices_to={'role': 'HOD'},
        help_text="Head of Department"
    )
    description = models.TextField(blank=True, help_text="Department description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """Course/Degree program model (e.g., B.Tech Computer Science)"""
    name = models.CharField(max_length=200, help_text="e.g., B.Tech Computer Science")
    code = models.CharField(max_length=20, unique=True, help_text="Course code (e.g., BTECH-CS)")
    duration_years = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Duration in years"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        help_text="Department offering this course"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):
    """Subject/Course subject model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, help_text="Subject code (e.g., CS101)")
    credits = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Credit hours"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Course this subject belongs to"
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester number"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Department offering this subject"
    )
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_taught',
        limit_choices_to={'role': 'FACULTY'},
        help_text="Faculty member teaching this subject"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['semester', 'code']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        unique_together = [['code', 'course']]

    def __str__(self):
        return f"{self.name} ({self.code}) - Sem {self.semester}"


class Enrollment(models.Model):
    """Student enrollment in a course"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Enrolled student"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Course enrolled in"
    )
    enrollment_date = models.DateField(help_text="Date of enrollment")
    current_semester = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Current semester"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    batch = models.CharField(max_length=50, help_text="e.g., 2024-2028")
    is_active = models.BooleanField(default=True, help_text="Whether enrollment is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-enrollment_date']
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        unique_together = [['student', 'course']]

    def __str__(self):
        return f"{self.student.username} - {self.course.name} ({self.batch})"


class TimeSlot(models.Model):
    """Time slot for timetable"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    start_time = models.TimeField(help_text="Class start time")
    end_time = models.TimeField(help_text="Class end time")
    day_of_week = models.IntegerField(choices=DAY_CHOICES, help_text="Day of week")
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        unique_together = [['day_of_week', 'start_time', 'end_time']]

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time} - {self.end_time}"


class Timetable(models.Model):
    """Timetable entry for a subject"""
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Subject"
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Time slot"
    )
    room = models.CharField(max_length=50, help_text="Room number/location")
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries',
        limit_choices_to={'role': 'FACULTY'},
        help_text="Faculty member (if different from subject faculty)"
    )
    batch = models.CharField(max_length=50, help_text="Batch (e.g., 2024-2028)")
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester"
    )
    academic_year = models.CharField(max_length=20, help_text="Academic year (e.g., 2024-2025)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time_slot__day_of_week', 'time_slot__start_time']
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return f"{self.subject.name} - {self.time_slot} - {self.room}"
    
    def check_conflicts(self):
        """Check for timetable conflicts (same faculty/room at same time)"""
        conflicts = Timetable.objects.filter(
            time_slot=self.time_slot,
            academic_year=self.academic_year,
            is_active=True
        ).exclude(pk=self.pk)
        
        faculty_conflicts = conflicts.filter(faculty=self.faculty) if self.faculty else Timetable.objects.none()
        room_conflicts = conflicts.filter(room=self.room)
        
        return {
            'faculty_conflicts': faculty_conflicts,
            'room_conflicts': room_conflicts,
            'has_conflicts': faculty_conflicts.exists() or room_conflicts.exists()
        }


class AcademicAdvisor(models.Model):
    """Model to map a faculty member as an advisor for a group of students in a semester"""
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='advised_classes',
        limit_choices_to={'role': 'FACULTY'},
        help_text="Faculty member designated as advisor"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='academic_advisors'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='academic_advisors'
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester number"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    section = models.CharField(max_length=10, blank=True, null=True, help_text="Section (optional, e.g., A, B)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-academic_year', 'semester', 'course']
        verbose_name = "Academic Advisor"
        verbose_name_plural = "Academic Advisors"
        # Only one active advisor per class per semester/year
        unique_together = [['course', 'semester', 'academic_year', 'section', 'is_active']]

    def __str__(self):
        section_str = f" - Sec {self.section}" if self.section else ""
        return f"{self.faculty.get_full_name()} | {self.course.code} Sem {self.semester}{section_str} ({self.academic_year})"


class StudyMaterial(models.Model):
    """Model for study materials uploaded by faculty"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='study_materials/')
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_materials_uploaded',
        limit_choices_to={'role': 'FACULTY'}
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='study_materials'
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Target semester"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_materials'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Study Material"
        verbose_name_plural = "Study Materials"

    def __str__(self):
        return f"{self.title} - {self.course.code} (Sem {self.semester})"

class TimetableDocument(models.Model):
    """Model for timetable documents uploaded by faculty"""
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='timetables/')
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timetables_uploaded',
        limit_choices_to={'role': 'FACULTY'}
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='timetable_documents'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='timetable_documents'
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Target semester"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    section = models.CharField(max_length=10, blank=True, null=True, help_text="Section (optional, e.g., A, B)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Timetable Document"
        verbose_name_plural = "Timetable Documents"

    def __str__(self):
        return f"{self.title} - {self.course.code} (Sem {self.semester})"
