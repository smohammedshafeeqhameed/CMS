from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import StudentProfile, SubjectEvaluation
from .forms import StudentProfileForm
from .evaluation_utils import get_ai_generated_questions, generate_ai_feedback, generate_ai_recommendations
from academics.models import Subject, Course, Department
from placements.models import JobPosting, Application
from django.views import View
import json


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student


class SubjectEvaluationListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = SubjectEvaluation
    template_name = 'students/evaluation_list.html'
    context_object_name = 'evaluations'

    def get_queryset(self):
        return SubjectEvaluation.objects.filter(student=self.request.user)


class InitiateEvaluationView(LoginRequiredMixin, StudentRequiredMixin, View):
    def get(self, request):
        # We can pre-filter based on student's current enrollment
        profile = request.user.student_profile
        subjects = Subject.objects.filter(course=profile.course, semester=profile.current_semester, is_active=True)
        return render(request, 'students/initiate_evaluation.html', {
            'subjects': subjects,
            'profile': profile
        })

    def post(self, request):
        subject_id = request.POST.get('subject')
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Simulate AI generating questions
        questions = get_ai_generated_questions(subject.name, subject.semester, subject.course.name)
        
        # Store questions in session for the test duration
        request.session['current_test'] = {
            'subject_id': subject.id,
            'questions': questions,
            'start_time': timezone.now().isoformat()
        }
        
        return redirect('take_evaluation')


class TakeEvaluationView(LoginRequiredMixin, StudentRequiredMixin, View):
    def get(self, request):
        test_data = request.session.get('current_test')
        if not test_data:
            messages.error(request, "No active test found. Please select a subject.")
            return redirect('initiate_evaluation')
            
        subject = get_object_or_404(Subject, id=test_data['subject_id'])
        return render(request, 'students/take_evaluation.html', {
            'subject': subject,
            'questions': test_data['questions']
        })

    def post(self, request):
        test_data = request.session.get('current_test')
        if not test_data:
            return redirect('initiate_evaluation')
            
        subject = get_object_or_404(Subject, id=test_data['subject_id'])
        questions = test_data['questions']
        
        correct_count = 0
        responses = []
        
        for idx, q in enumerate(questions):
            ans = request.POST.get(f'q_{idx}')
            is_correct = ans == q['correct']
            if is_correct:
                correct_count += 1
            
            responses.append({
                'question': q['question'],
                'user_answer': ans,
                'correct_answer': q['correct'],
                'is_correct': is_correct,
                'explanation': q['explanation']
            })
            
        total = len(questions)
        score_percent = (correct_count / total) * 100 if total > 0 else 0
        
        # AI Logic: Feedback and Recommendations
        ai_feedback = generate_ai_feedback(score_percent, subject.name)
        ai_recommendations = generate_ai_recommendations(score_percent, subject.name)
        
        # Save to database
        evaluation = SubjectEvaluation.objects.create(
            student=request.user,
            subject=subject,
            course=subject.course,
            semester=subject.semester,
            score=score_percent,
            total_questions=total,
            correct_answers=correct_count,
            ai_feedback=ai_feedback,
            ai_recommendations=ai_recommendations,
            test_details={'responses': responses}
        )
        
        # Clear session
        del request.session['current_test']
        
        return redirect('evaluation_detail', pk=evaluation.id)


class EvaluationDetailView(LoginRequiredMixin, View):
    """View result and AI feedback. Accessible by student, faculty, and HOD."""
    def get(self, request, pk):
        evaluation = get_object_or_404(SubjectEvaluation, pk=pk)
        
        # Permissions: Student can see their own. Faculty and HOD can see their mentees.
        can_view = False
        if request.user == evaluation.student:
            can_view = True
        elif request.user.role in ['FACULTY', 'HOD']:
            # For simplicity, check department match (could be more strict with advisor mapping)
            if request.user.department_fk == evaluation.student.department_fk:
                can_view = True
        
        if not can_view:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
            
        return render(request, 'students/evaluation_result.html', {
            'evaluation': evaluation,
            'details': evaluation.test_details.get('responses', [])
        })


class StudentProfileView(LoginRequiredMixin, DetailView):
    model = StudentProfile
    template_name = 'students/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        user = profile.user
        
        # Fetch relevant job postings based on department
        if user.department_fk:
            # We filter by department name (Char comparison) as JobPosting stores it as CharField
            relevant_jobs = JobPosting.objects.filter(
                Q(department__icontains=user.department_fk.name) | Q(department__icontains=user.department_fk.code) | Q(department=""),
                is_active=True,
                deadline__gte=timezone.now()
            ).order_by('-created_at')[:5] # Show top 5 recent jobs
            context['relevant_jobs'] = relevant_jobs
            
        # Add Announcements for Notice Board
        from announcements.models import Announcement
        context['personal_posts'] = Announcement.objects.filter(
            target_individual=user,
            is_active=True
        ).order_by('-posted_at')[:5]
        context['general_announcements'] = Announcement.objects.filter(
            target_audience__in=['ALL', 'STUDENTS'],
            is_active=True
        ).exclude(target_individual=user).order_by('-posted_at')[:5]
            
        # Add Library Records
        from library.models import BorrowRecord, Fine
        context['library_records'] = BorrowRecord.objects.filter(user=user).order_by('-request_date')[:5]
        context['active_borrows_count'] = BorrowRecord.objects.filter(user=user, status__in=['ISSUED', 'OVERDUE']).count()
        context['overdue_count'] = BorrowRecord.objects.filter(user=user, status='OVERDUE').count()
        context['total_fine'] = Fine.objects.filter(borrow_record__user=user, paid=False).aggregate(total=Sum('amount'))['total'] or 0.00
            
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            profile = get_object_or_404(StudentProfile, pk=pk)
            user = self.request.user
            
            # Authorization logic
            if user.role == 'STUDENT' and user.student_profile != profile:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied
            
            if user.role in ['FACULTY', 'HOD']:
                if user.department_fk != profile.user.department_fk:
                    from django.core.exceptions import PermissionDenied
                    raise PermissionDenied
            return profile
            
        return self.request.user.student_profile

class StudentProfileUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'students/profile_form.html'
    success_url = reverse_lazy('student_profile')

    def get_object(self):
        return self.request.user.student_profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class InternshipListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = JobPosting
    template_name = 'students/internship_list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

    def get_queryset(self):
        return JobPosting.objects.filter(is_active=True, deadline__gte=timezone.now()).order_by('-created_at')

class InternshipDetailView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = JobPosting
    template_name = 'students/internship_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if student has already applied
        context['has_applied'] = Application.objects.filter(
            student=self.request.user, 
            job=self.object
        ).exists()
        return context

class ApplicationListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Application
    template_name = 'students/application_list.html'
    context_object_name = 'applications'
    ordering = ['-applied_at']

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user).select_related('job').order_by('-applied_at')

def apply_job(request, job_id):
    if not request.user.is_authenticated or not request.user.is_student:
        return redirect('login')
    
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, id=job_id)
        
        # Check if already applied
        if Application.objects.filter(student=request.user, job=job).exists():
            messages.warning(request, "You have already applied for this position.")
        else:
            Application.objects.create(student=request.user, job=job)
            messages.success(request, f"Successfully applied to {job.title} at {job.company}!")
        
        return redirect('internship_detail', pk=job.id)
    
    return redirect('internship_list')
