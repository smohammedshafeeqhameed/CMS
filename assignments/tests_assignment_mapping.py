from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from academics.models import Department, Course, Subject, Enrollment
from assignments.models import Assignment, AssignmentSubmission

User = get_user_model()

class AssignmentSystemTest(TestCase):
    def setUp(self):
        # Create department and course
        self.dept = Department.objects.create(name="Engineering", code="ENG")
        self.course = Course.objects.create(name="B.E. Mech", code="BE-MECH", department=self.dept)
        
        # Create users
        self.faculty = User.objects.create_user(username="faculty1", password="password", role="FACULTY")
        self.student = User.objects.create_user(username="student1", password="password", role="STUDENT")
        
        # Enroll student
        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            enrollment_date=timezone.now().date(),
            current_semester=1,
            academic_year="2024-2025"
        )
        
        # Create subject taught by faculty
        self.subject = Subject.objects.create(
            name="Thermodynamics",
            code="ME101",
            course=self.course,
            semester=1,
            department=self.dept,
            faculty=self.faculty
        )

    def test_assignment_mapping(self):
        # Create assignment
        assignment = Assignment.objects.create(
            title="Unit 1 Quiz",
            description="Test assignment",
            subject=self.subject,
            faculty=self.faculty,
            due_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Verify assignment creation
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertEqual(assignment.faculty, self.faculty)
        
    def test_submission_logic(self):
        assignment = Assignment.objects.create(
            title="Unit 1 Quiz",
            description="Test assignment",
            subject=self.subject,
            faculty=self.faculty,
            due_date=timezone.now() + timezone.timedelta(days=7)
        )
        
        # Student submits
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_file="submissions/test.pdf"
        )
        
        self.assertEqual(AssignmentSubmission.objects.count(), 1)
        self.assertFalse(submission.is_late)
        
    def test_late_submission(self):
        # Past due date
        assignment = Assignment.objects.create(
            title="Late Quiz",
            description="Test assignment",
            subject=self.subject,
            faculty=self.faculty,
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_file="submissions/test_late.pdf"
        )
        
        self.assertTrue(submission.is_late)
