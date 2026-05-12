import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Department, Course, Subject
from students.models import StudentProfile, SubjectEvaluation
from marks.models import InternalMark, AssessmentType

User = get_user_model()

def run_diagnostic():
    try:
        print("Creating Department...")
        dept = Department.objects.create(name="Diag Dept", code="DD")
        
        print("Creating Faculty...")
        faculty = User.objects.create_user(username='diag_faculty', role='FACULTY', department_fk=dept)
        
        print("Creating Course...")
        course = Course.objects.create(name="Diag Course", code="DC", department=dept)
        
        print("Creating Subject...")
        subject = Subject.objects.create(name="Diag Subject", code="DS", course=course, semester=1, department=dept)
        
        print("Creating Student...")
        student = User.objects.create_user(username='diag_student', role='STUDENT', department_fk=dept)
        
        print("Creating StudentProfile...")
        profile = StudentProfile.objects.create(user=student, skills="Test", cgpa=9.0, enrollment_number="DIAG001")
        
        print("Creating AssessmentType...")
        at = AssessmentType.objects.create(name="Diag Test", weightage=10)
        
        print("Creating InternalMark...")
        InternalMark.objects.create(
            student=student, subject=subject, assessment_type=at,
            marks_obtained=10, max_marks=10, semester=1,
            academic_year="2024-2025", assessment_date="2024-03-01"
        )
        
        print("Creating SubjectEvaluation...")
        SubjectEvaluation.objects.create(
            student=student, subject=subject, course=course, semester=1,
            score=100, total_questions=1, correct_answers=1
        )
        
        print("Success!")
    except Exception as e:
        print(f"FAILED at: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostic()
