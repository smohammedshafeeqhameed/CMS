from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, AssignmentSubmissionForm, GradeSubmissionForm
from users.mixins import FacultyRequiredMixin, StudentRequiredMixin
from academics.models import Enrollment, Subject

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_faculty:
            return Assignment.objects.filter(faculty=user)
        elif user.role == 'STUDENT':
            # Try Enrollment first
            enrollment = Enrollment.objects.filter(student=user, is_active=True).first()
            if enrollment:
                return Assignment.objects.filter(
                    subject__course=enrollment.course,
                    subject__semester=enrollment.current_semester,
                    is_active=True
                )
            # Fallback to StudentProfile
            profile = getattr(user, 'student_profile', None)
            if profile:
                return Assignment.objects.filter(
                    subject__course=profile.course,
                    subject__semester=profile.current_semester,
                    is_active=True
                )
        return Assignment.objects.none()

class AssignmentCreateView(LoginRequiredMixin, FacultyRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    success_url = reverse_lazy('assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.faculty = self.request.user
        messages.success(self.request, "Assignment created successfully.")
        return super().form_valid(form)

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_student:
            submission = AssignmentSubmission.objects.filter(
                assignment=self.object,
                student=self.request.user
            ).first()
            context['submission'] = submission
            if not submission:
                context['submission_form'] = AssignmentSubmissionForm()
        return context

class AssignmentSubmissionView(LoginRequiredMixin, StudentRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        
        # Check if already submitted
        if AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).exists():
            messages.error(request, "You have already submitted this assignment.")
            return redirect('assignment_detail', pk=assignment.pk)
        
        # Check if overdue
        if assignment.is_overdue():
             messages.error(request, "Deadline has passed. Cannot submit.")
             return redirect('assignment_detail', pk=assignment.pk)

        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.save()
                messages.success(request, "Assignment submitted successfully.")
            except Exception as e:
                messages.error(request, f"Error saving submission: {str(e)}")
        else:
            messages.error(request, "Error in submission. Please check the file and remarks.")
        
        return redirect('assignment_detail', pk=assignment.pk)

class SubmissionListView(LoginRequiredMixin, FacultyRequiredMixin, ListView):
    model = AssignmentSubmission
    template_name = 'assignments/submission_list.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'], faculty=self.request.user)
        return AssignmentSubmission.objects.filter(assignment=assignment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignment, pk=self.kwargs['pk'])
        return context

class GradeSubmissionView(LoginRequiredMixin, FacultyRequiredMixin, UpdateView):
    model = AssignmentSubmission
    form_class = GradeSubmissionForm
    template_name = 'assignments/grade_form.html'
    context_object_name = 'submission'
    
    def get_success_url(self):
        return reverse_lazy('submission_list', kwargs={'pk': self.object.assignment.pk})

    def form_valid(self, form):
        form.instance.graded_by = self.request.user
        form.instance.graded_at = timezone.now()
        messages.success(self.request, "Submission graded successfully.")
        return super().form_valid(form)
