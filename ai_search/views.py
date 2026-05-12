import json
import os
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
try:
    from openai import OpenAI
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    client = None

class PDFChatAssistantView(View):
    def post(self, request):
        # Determine if it's an upload, reset, or a chat request
        if 'pdf_file' in request.FILES:
            return self.handle_upload(request)
        
        try:
            data = json.loads(request.body)
            if data.get('action') == 'reset':
                request.session['pdf_context'] = ''
                request.session['pdf_filename'] = ''
                return JsonResponse({'status': 'success', 'message': 'Context cleared.'})
        except:
            pass

        return self.handle_chat(request)

    def handle_upload(self, request):
        try:
            pdf_file = request.FILES['pdf_file']
            
            # Read PDF content
            reader = PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            if not full_text.strip():
                return JsonResponse({'status': 'error', 'message': 'Could not extract text from the PDF. It might be empty or image-based.'}, status=400)
            
            # Store in session (limited size, but usually okay for moderate PDFs)
            # For very large PDFs, one should use a database or vector store.
            # Truncate to avoid session size limits if necessary (OpenAI also has token limits)
            request.session['pdf_context'] = full_text[:50000] # Safe limit for session and context
            request.session['pdf_filename'] = pdf_file.name
            
            return JsonResponse({
                'status': 'success', 
                'message': f'PDF "{pdf_file.name}" uploaded and processed successfully!',
                'filename': pdf_file.name
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def handle_chat(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            pdf_context = request.session.get('pdf_context', '')
            pdf_filename = request.session.get('pdf_filename', '')
            
            if pdf_context:
                system_prompt = f"""
                You are a professional AI Assistant specialized in analyzing documents.
                A document named "{pdf_filename}" has been uploaded.
                
                Instructions:
                1. Primarily use the extracted text below to answer questions.
                2. Be professional, concise, and helpful.
                3. If the answer is not in the document but is a general professional or academic question, you may provide a general answer but mention it's not from the document.
                4. If the info IS in the document, definitely use it.
                
                Document Content:
                {pdf_context}
                """
            else:
                system_prompt = """
                You are a professional AI Assistant for the EduPulse College Management System.
                Your goal is to assist students, faculty, and staff with their professional and academic queries.
                
                Instructions:
                1. Maintain a highly professional, helpful, and concise tone.
                2. If the user wants to analyze a specific document, remind them they can upload a PDF using the attachment icon.
                """
                
                # Role-specific context injection
                user = request.user
                if hasattr(user, 'is_faculty') and user.is_faculty:
                    from academics.models import AcademicAdvisor
                    from students.models import StudentProfile, SubjectEvaluation
                    from marks.models import InternalMark
                    from interviews.models import InterviewSchedule
                    from django.contrib.auth import get_user_model
                    from django.db.models import Avg
                    User = get_user_model()
                    
                    # Fetch student data for the faculty's department or mentees
                    if user.department_fk:
                        student_users = User.objects.filter(role='STUDENT', department_fk=user.department_fk).select_related('student_profile')
                    else:
                        assignments = AcademicAdvisor.objects.filter(faculty=user, is_active=True)
                        if assignments.exists():
                            profiles = StudentProfile.objects.filter(
                                course__in=assignments.values_list('course', flat=True),
                                current_semester__in=assignments.values_list('semester', flat=True)
                            )
                            student_users = User.objects.filter(student_profile__in=profiles).select_related('student_profile')
                        else:
                            student_users = User.objects.none()
                    
                    students_list = []
                    for s in student_users:
                        # Skills
                        skills = s.student_profile.skills if hasattr(s, 'student_profile') and s.student_profile else "N/A"
                        
                        # Exam performance (Internal Marks average percentage)
                        marks = InternalMark.objects.filter(student=s)
                        if marks.exists():
                            total_obtained = float(sum(m.marks_obtained for m in marks))
                            total_max = float(sum(m.max_marks for m in marks))
                            exam_avg = (total_obtained / total_max) * 100 if total_max > 0 else 0
                        else:
                            exam_avg = 0
                            
                        # Mock Interview performance (AI Subject Evaluations)
                        evals = SubjectEvaluation.objects.filter(student=s)
                        mock_avg = float(evals.aggregate(Avg('score'))['score__avg'] or 0)
                        
                        # Latest AI Evaluation Detail (corresponds to /student/evaluations/result/)
                        latest_eval = evals.order_by('-created_at').first()
                        eval_feedback = latest_eval.ai_feedback if latest_eval else "N/A"
                        
                        # CGPA and Attendance
                        cgpa = float(s.student_profile.cgpa or 0) if hasattr(s, 'student_profile') and s.student_profile else 0
                        attendance = float(s.attendance or 0)
                        
                        # Placement Mock Interview performance (InterviewSchedule)
                        interviews = InterviewSchedule.objects.filter(application__student=s, status='COMPLETED').order_by('-date_time')
                        placement_feedback = interviews.first().feedback if interviews.exists() else "No feedback yet"
                        
                        students_list.append({
                            'name': s.get_full_name() or s.username,
                            'id': s.username,
                            'skills': skills,
                            'exam_avg': round(exam_avg, 2),
                            'mock_avg': round(mock_avg, 2),
                            'latest_eval_feedback': eval_feedback[:150] + "..." if len(eval_feedback) > 150 else eval_feedback,
                            'placement_feedback': placement_feedback[:150] + "..." if len(placement_feedback) > 150 else placement_feedback,
                            'cgpa': cgpa,
                            'attendance': attendance
                        })
                    
                    if students_list:
                        student_data_str = "\n".join([
                            f"- {s['name']} (ID: {s['id']}): Skills: {s['skills']}, Exam Avg: {s['exam_avg']}%, Mock Interview (Subject) Avg: {s['mock_avg']}%, AI Evaluation Feedback: {s['latest_eval_feedback']}, Placement Mock Feedback: {s['placement_feedback']}, CGPA: {s['cgpa']}, Attendance: {s['attendance']}%"
                            for s in students_list
                        ])
                        
                        system_prompt += f"""
                        
                        Faculty Specific Context (Student Performance & Skills):
                        You have access to the following students in your department/mentorship:
                        {student_data_str}
                        
                        Special Instructions for Faculty Queries:
                        1. **Finding Capable Students**: When asked for students with a specific skill, search the 'Skills' field. Recommend students who have that skill and also have good academic standing (CGPA/Marks).
                        2. **Best in Exams**: Identify top performers based on 'Exam Avg' and 'CGPA'.
                        3. **Career Readiness**: Use 'Mock Interview (Subject) Avg', 'AI Evaluation Feedback' (from subject-specific tests), and 'Placement Mock Feedback' to assess a student's readiness and specific strengths/weaknesses.
                        4. **Result Analysis**: If asked about a student's performance in a specific test or evaluation result, use the 'AI Evaluation Feedback' provided for context on what they did well or where they need improvement.
                        5. **Volunteering/Recommendations**: Prioritize students with high attendance (above 85%) and strong overall performance. Do NOT recommend students with attendance below 75% for extra-curriculur tasks.
                        6. Provide a clear rationale for your recommendations based on the data provided above.
                        """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600
            )
            
            ai_message = response.choices[0].message.content
            return JsonResponse({'status': 'success', 'message': ai_message})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
