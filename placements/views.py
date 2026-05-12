from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q
from django.contrib import messages
from .models import JobPosting, Application
from .forms import JobPostingForm
from users.models import User
from students.models import StudentProfile, Certificate

class PlacementRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_placement_cell or self.request.user.is_placement_officer)

class ApplicationListView(LoginRequiredMixin, PlacementRequiredMixin, ListView):
    model = Application
    template_name = 'placements/application_list.html'
    context_object_name = 'applications'
    ordering = ['-applied_at']

    def get_queryset(self):
        # Filter by job if provided
        job_id = self.request.GET.get('job_id')
        if job_id:
            return Application.objects.filter(job_id=job_id).order_by('-applied_at')
        return Application.objects.all().order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = JobPosting.objects.all()
        return context

class JobPostingListView(LoginRequiredMixin, PlacementRequiredMixin, ListView):
    model = JobPosting
    template_name = 'placements/manage_jobs.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

    def get_queryset(self):
        # Allow checking all jobs posted
        return JobPosting.objects.all().order_by('-created_at')

class JobPostingCreateView(LoginRequiredMixin, PlacementRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'placements/job_form.html'
    success_url = reverse_lazy('manage_jobs')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

class JobPostingUpdateView(LoginRequiredMixin, PlacementRequiredMixin, UpdateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'placements/job_form.html'
    success_url = reverse_lazy('manage_jobs')

class JobPostingDeleteView(LoginRequiredMixin, PlacementRequiredMixin, DeleteView):
    model = JobPosting
    template_name = 'placements/job_confirm_delete.html'
    success_url = reverse_lazy('manage_jobs')

class PlacementAnalyticsView(LoginRequiredMixin, PlacementRequiredMixin, TemplateView):
    template_name = 'placements/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Key Metrics
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_postings'] = JobPosting.objects.count()
        context['total_applications'] = Application.objects.count()
        context['placed_students'] = Application.objects.filter(status='OFFERED').values('student').distinct().count()

        # Data for Charts
        # 1. Applications per Job (Top 5)
        jobs_popularity = JobPosting.objects.annotate(app_count=Count('applications')).order_by('-app_count')[:5]
        context['job_labels'] = [job.title for job in jobs_popularity]
        context['job_data'] = [job.app_count for job in jobs_popularity]

        # 2. Status Distribution
        status_dist = Application.objects.values('status').annotate(count=Count('status'))
        context['status_dist'] = list(status_dist) # [{'status': 'APPLIED', 'count': 10}, ...]

        return context

# -----------------------------------------------------------------------------
# Student Management & Verification Views
# -----------------------------------------------------------------------------

class StudentListView(LoginRequiredMixin, PlacementRequiredMixin, ListView):
    model = User
    template_name = 'placements/student_list.html'
    context_object_name = 'students'
    ordering = ['username']

    def get_queryset(self):
        # We want to list users who are STUDENTS, and preferably those who have a profile
        return User.objects.filter(role='STUDENT').select_related('student_profile')

class StudentDetailView(LoginRequiredMixin, PlacementRequiredMixin, DetailView):
    model = User
    template_name = 'placements/student_detail.html'
    context_object_name = 'student_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # Get profiles if exists
        profile = getattr(user, 'student_profile', None)
        context['profile'] = profile
        # Get certificates
        context['certificates'] = Certificate.objects.filter(student=user)
        
        # Process skills into a list for the template
        if profile and profile.skills:
            context['skills_list'] = [s.strip() for s in profile.skills.split(',') if s.strip()]
            
        return context

class VerifyCertificateView(LoginRequiredMixin, PlacementRequiredMixin, View):
    def post(self, request, pk):
        cert = get_object_or_404(Certificate, pk=pk)
        
        # Mark as verified
        cert.is_verified = True
        cert.save()
        
        messages.success(request, f"Certificate '{cert.name}' verified and skill badge generated successfully!")
        
        # Redirect back to the student detail page
        return redirect('student_detail', pk=cert.student.pk)
