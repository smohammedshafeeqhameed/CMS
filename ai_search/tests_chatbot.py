from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from ai_search.views import PDFChatAssistantView
from academics.models import Department, Course, Subject
from students.models import StudentProfile, SubjectEvaluation
from marks.models import InternalMark, AssessmentType
import json
from unittest.mock import patch, MagicMock
import traceback

User = get_user_model()

class ChatbotFacultyContextTest(TestCase):
    def setUp(self):
        try:
            self.factory = RequestFactory()
            self.dept = Department.objects.create(name="Computer Science", code="CS")
            self.faculty = User.objects.create_user(
                username='faculty1', 
                password='password', 
                role='FACULTY',
                department_fk=self.dept
            )
            
            self.course = Course.objects.create(name="B.Tech CS", code="BTCS", department=self.dept)
            self.subject = Subject.objects.create(name="Python", code="CS101", course=self.course, semester=1, department=self.dept)
            
            self.student = User.objects.create_user(
                username='student1', 
                password='password', 
                role='STUDENT',
                department_fk=self.dept
            )
            # StudentProfile is created via SIGNAL
            self.profile = self.student.student_profile
            self.profile.skills = "Python, Django"
            self.profile.cgpa = 9.5
            self.profile.enrollment_number = "EN001"
            self.profile.save()
            
            self.assessment = AssessmentType.objects.create(name="Quiz", weightage=20)
            InternalMark.objects.create(
                student=self.student,
                subject=self.subject,
                assessment_type=self.assessment,
                marks_obtained=18,
                max_marks=20,
                semester=1,
                academic_year="2024-2025",
                assessment_date="2024-03-01"
            )
            
            SubjectEvaluation.objects.create(
                student=self.student,
                subject=self.subject,
                course=self.course,
                semester=1,
                score=90,
                total_questions=10,
                correct_answers=9
            )
        except Exception as e:
            print(f"Error in setUp: {e}")
            traceback.print_exc()
            raise

    @patch('ai_search.views.client')
    def test_faculty_context_injection(self, mock_client):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Recommendation: student1"
        mock_client.chat.completions.create.return_value = mock_response
        
        request = self.factory.post('/ai_search/assistant/', 
                                   data=json.dumps({'message': 'Who is good at Python?'}),
                                   content_type='application/json')
        request.user = self.faculty
        request.session = {}
        
        view = PDFChatAssistantView()
        response = view.post(request)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that client.chat.completions.create was called with the injected context
        args, kwargs = mock_client.chat.completions.create.call_args
        messages = kwargs['messages']
        system_msg = next(m for m in messages if m['role'] == 'system')['content']
        
        self.assertIn("student1", system_msg)
        self.assertIn("Python, Django", system_msg)
        self.assertIn("Skills:", system_msg)
        self.assertIn("Exam Avg: 90.0%", system_msg)
        self.assertIn("Mock Interview Avg: 90.0%", system_msg)
