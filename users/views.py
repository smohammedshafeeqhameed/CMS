from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import (
    CustomUserCreationForm, FacultyCreationForm, 
    AdminCreationForm, AdminStudentCreationForm
)
from .models import User
from .mixins import AdminRequiredMixin, SuperAdminRequiredMixin, HODRequiredMixin
from .utils import send_approval_email
from library.models import BorrowRecord

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Set session to expire when browser closes
            self.request.session.set_expiry(0)
        else:
            # Set session to expire in 2 weeks
            self.request.session.set_expiry(1209600)  # 14 days in seconds
        return super().form_valid(form)

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Account must be approved by admin
        user.is_approved = False
        user.save()
        messages.success(self.request, "Account created successfully! Please wait for admin approval before logging in.")
        return redirect(self.success_url)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_template_names(self):
        role = self.request.user.role
        if role == 'SUPER_ADMIN':
            return ['users/dashboards/super_admin.html']
        elif role == 'ADMIN':
            return ['users/dashboards/admin.html']
        elif role == 'HOD':
            return ['users/dashboards/hod.html']
        elif role == 'FACULTY':
            return ['users/dashboards/faculty.html']
        elif role == 'STUDENT':
            return ['users/dashboards/student.html']
        elif role == 'PLACEMENT_OFFICER' or role == 'PLACEMENT_CELL':
            return ['users/dashboards/placement_officer.html']
        elif role == 'INDUSTRY' or role == 'EMPLOYER':
            return ['users/dashboards/industry.html']
        elif role == 'LIBRARIAN':
            return ['users/dashboards/librarian.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['role'] = user.get_role_display()
        context['user'] = user
        
        # Role-specific context
        if user.is_student:
            context.update(self.get_student_context())
        elif user.is_faculty:
            context.update(self.get_faculty_context())
        elif user.is_super_admin or user.is_admin:
            context.update(self.get_admin_context())
        elif user.is_hod:
            context.update(self.get_hod_context())
        elif user.is_placement_cell or user.is_placement_officer:
            context.update(self.get_placement_context())
        elif user.is_industry or user.is_employer:
            context.update(self.get_industry_context())
        elif user.is_librarian:
            context.update(self.get_librarian_context())
        
        return context
    
    def get_industry_context(self):
        """Context for industry partner dashboard"""
        from placements.models import JobPosting, Application
        
        return {
            'active_jobs': JobPosting.objects.filter(company_user=self.request.user, is_active=True).count() if hasattr(JobPosting.objects, 'company_user') else 0,
            'total_applications': Application.objects.filter(job__company_user=self.request.user).count() if hasattr(JobPosting.objects, 'company_user') else 0,
            'matched_students': User.objects.filter(role='STUDENT', is_approved=True).count(), # Simplification
        }
    
    def get_student_context(self):
        """Context for student dashboard"""
        from placements.models import Application, JobPosting
        from interviews.models import InterviewSchedule
        from announcements.models import Announcement
        from academics.models import StudyMaterial
        from django.utils import timezone
        
        from django.db.models import Q
        user = self.request.user
        
        # Proper context-aware announcements for dashboard
        q_filter = Q(target_audience='ALL') | Q(target_audience='STUDENTS')
        if hasattr(user, 'student_profile') and user.student_profile.course:
            q_filter |= Q(target_audience='DEPARTMENT', target_department=user.student_profile.course.department)
            if user.student_profile.batch:
                q_filter |= Q(target_audience='BATCH', target_batch=user.student_profile.batch)
        
        # Exclude personal posts from general ones to avoid duplication
        general_announcements = Announcement.objects.filter(
            q_filter, 
            is_active=True
        ).exclude(target_audience='INDIVIDUAL').order_by('-is_pinned', '-posted_at')[:5]

        personal_posts = Announcement.objects.filter(
            target_audience='INDIVIDUAL',
            target_individual=user,
            is_active=True
        ).order_by('-posted_at')[:5]

        from assignments.models import Assignment
        
        # Calculate assignments count
        assignments_count = 0
        if hasattr(user, 'student_profile') and user.student_profile.course:
            assignments_count = Assignment.objects.filter(
                subject__course=user.student_profile.course,
                subject__semester=user.student_profile.current_semester,
                is_active=True,
                due_date__gte=timezone.now()
            ).count()

        return {
            'pending_applications': Application.objects.filter(
                student=user, 
                status='APPLIED'
            ).count(),
            'upcoming_interviews': InterviewSchedule.objects.filter(
                application__student=user,
                status='SCHEDULED',
                date_time__gte=timezone.now()
            ).count(),
            'active_jobs': JobPosting.objects.filter(
                is_active=True,
                deadline__gte=timezone.now()
            ).count(),
            'assignments_count': assignments_count,
            'profile_completeness': getattr(
                user, 'student_profile', None
            ).get_profile_completeness() if hasattr(user, 'student_profile') else 0,
            'personal_posts': personal_posts,
            'general_announcements': general_announcements,
            'recent_materials': StudyMaterial.objects.filter(
                department=user.department_fk,
                course=getattr(user, 'student_profile').course,
                semester=getattr(user, 'student_profile').current_semester
            ).select_related('faculty', 'subject')[:4] if hasattr(user, 'student_profile') and user.student_profile.course else [],
            'recent_assignments': Assignment.objects.filter(
                subject__course=getattr(user, 'student_profile').course,
                subject__semester=getattr(user, 'student_profile').current_semester,
                is_active=True,
                due_date__gte=timezone.now()
            ).select_related('faculty', 'subject').order_by('due_date')[:4] if hasattr(user, 'student_profile') and user.student_profile.course else [],
        }
    
    def get_faculty_context(self):
        """Context for faculty dashboard"""
        from academics.models import AcademicAdvisor, StudyMaterial
        from students.models import StudentProfile
        from placements.models import Application
        
        # Get all active assignments/mappings for this faculty
        assignments = AcademicAdvisor.objects.filter(faculty=self.request.user, is_active=True).select_related('course')
        
        # Build query for students based on assignments
        mentee_profiles = StudentProfile.objects.none()
        for assignment in assignments:
            # Match students by course and semester
            class_mentees = StudentProfile.objects.filter(
                course=assignment.course,
                current_semester=assignment.semester
            )
            mentee_profiles = mentee_profiles | class_mentees
            
        # Get actual User objects for these profiles
        mentees = User.objects.filter(student_profile__in=mentee_profiles).select_related('student_profile')
        
        # Get taught subjects
        taught_subjects = self.request.user.subjects_taught.filter(is_active=True).select_related('course')
        
        from announcements.models import Announcement
        from django.db.models import Q
        user = self.request.user
        
        # Proper context-aware announcements for faculty
        q_filter = Q(target_audience='ALL') | Q(target_audience='FACULTY')
        if user.department_fk:
            q_filter |= Q(target_audience='DEPARTMENT', target_department=user.department_fk)
            
        announcements = Announcement.objects.filter(
            q_filter,
            is_active=True
        ).order_by('-is_pinned', '-posted_at')[:5]
        
        return {
            'pending_approvals': Application.objects.filter(
                faculty_approved=False,
                status='APPLIED'
            ).count(),
            'mentees': mentees,
            'assignments': assignments,
            'total_students': mentees.count(),
            'taught_subjects': taught_subjects,
            'today_date': timezone.now().date().isoformat(),
            'assigned_courses': assignments.values('course__id', 'course__name', 'course__code').distinct(),
            'assigned_semesters': assignments.values_list('semester', flat=True).distinct().order_by('semester'),
            'library_records': BorrowRecord.objects.filter(user=user).order_by('-request_date')[:5],
            'announcements': announcements,
            'recent_materials': StudyMaterial.objects.filter(faculty=user).select_related('course', 'subject')[:5],
        }
    
    def get_admin_context(self):
        """Context for admin/super admin dashboard"""
        from academics.models import Department, Course
        from placements.models import JobPosting, Application
        from students.models import StudentProfile
        from django.db.models import Count, Q
        
        # Basic Stats
        user = self.request.user
        pending_approvals_query = User.objects.filter(is_approved=False, is_active=False)
        
        if user.role == 'SUPER_ADMIN':
            # Super Admin sees non-students
            pending_count = pending_approvals_query.exclude(role='STUDENT').count()
        elif user.role == 'ADMIN':
            # Admin sees only students
            pending_count = pending_approvals_query.filter(role='STUDENT').count()
        else:
            pending_count = pending_approvals_query.count()

        # Announcement feed
        from announcements.models import Announcement
        
        context = {
            'total_users': User.objects.count(),
            'pending_approvals_count': pending_count,
            'total_departments': Department.objects.filter(is_active=True).count() if Department.objects.exists() else 0,
            'active_jobs': JobPosting.objects.filter(is_active=True).count() if JobPosting.objects.exists() else 0,
            'total_applications': Application.objects.count() if Application.objects.exists() else 0,
            'announcements': Announcement.objects.filter(is_active=True).order_by('-is_pinned', '-posted_at')[:5],
        }

        # Academic Performance Analytics (Pass/Fail)
        # Logic: CGPA > 0 is Pass, CGPA == 0 is Fail
        
        # 1. Overall Pass/Fail
        profiles = StudentProfile.objects.all()
        passed_count = profiles.filter(cgpa__gt=0).count()
        failed_count = profiles.filter(cgpa=0).count()
        context['overall_pass_fail'] = [
            {'status': 'Passed', 'count': passed_count},
            {'status': 'Failed', 'count': failed_count}
        ]

        # 2. Department-wise Pass Percentage
        dept_data = []
        for dept in Department.objects.filter(is_active=True):
            total = StudentProfile.objects.filter(course__department=dept).count()
            if total > 0:
                passed = StudentProfile.objects.filter(course__department=dept, cgpa__gt=0).count()
                dept_data.append({
                    'label': dept.code,
                    'percentage': round((passed / total) * 100, 1)
                })
        context['dept_pass_rates'] = dept_data

        # 3. Course-wise Pass Percentage
        course_data = []
        for course in Course.objects.filter(is_active=True):
            total = StudentProfile.objects.filter(course=course).count()
            if total > 0:
                passed = StudentProfile.objects.filter(course=course, cgpa__gt=0).count()
                course_data.append({
                    'label': course.code,
                    'percentage': round((passed / total) * 100, 1)
                })
        context['course_pass_rates'] = course_data

        return context
    
    def get_hod_context(self):
        """Context for HOD dashboard"""
        from academics.models import Department
        
        # Priority 1: Department where the user is explicitly set as HOD
        dept = self.request.user.departments_headed.first()
        
        # Priority 2: Department set on the user's profile
        if not dept:
            dept = self.request.user.department_fk
            
        if not dept:
            return {}
        
        from announcements.models import Announcement
        recent_announcements = Announcement.objects.filter(
            posted_by=self.request.user
        ).order_by('-posted_at')[:5]

        return {
            'department': dept,
            'faculty_count': dept.members.filter(role='FACULTY', is_approved=True).count(),
            'student_count': dept.members.filter(role='STUDENT', is_approved=True).count(),
            'faculties': dept.members.filter(role='FACULTY').order_by('is_approved', 'last_name'),
            'students': dept.members.filter(role='STUDENT').order_by('is_approved', 'last_name'),
            'pending_faculty_approvals': dept.members.filter(
                role='FACULTY',
                is_approved=False
            ).count(),
            'pending_student_approvals': dept.members.filter(
                role='STUDENT',
                is_approved=False
            ).count(),
            'recent_announcements': recent_announcements,
        }
    
    def get_placement_context(self):
        """Context for placement officer dashboard"""
        from placements.models import JobPosting, Application
        from django.utils import timezone
        
        return {
            'active_jobs': JobPosting.objects.filter(is_active=True).count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(
                status='APPLIED'
            ).count(),
            'upcoming_interviews': Application.objects.filter(
                status='INTERVIEW'
            ).count(),
        }
    
    def get_librarian_context(self):
        """Context for librarian dashboard"""
        from library.models import Book, BorrowRecord
        
        return {
            'total_books': Book.objects.count(),
            'total_issued': BorrowRecord.objects.filter(status='ISSUED').count(),
            'total_overdue': BorrowRecord.objects.filter(status='OVERDUE').count(),
            'pending_requests': BorrowRecord.objects.filter(status='PENDING').count(),
            'recent_transactions': BorrowRecord.objects.select_related('user', 'book').order_by('-request_date')[:5],
        }
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is approved
        if request.user.is_authenticated and not request.user.is_approved and request.user.role not in ['STUDENT', 'SUPER_ADMIN', 'ADMIN']:
            from django.contrib import messages
            messages.warning(request, "Your account is pending approval. Please wait for admin approval.")
        return super().dispatch(request, *args, **kwargs)

class UserApprovalListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    """List view for pending user approvals"""
    model = User
    template_name = 'users/user_approval.html'
    context_object_name = 'pending_users'
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(is_approved=False, is_active=False).order_by('-date_joined')
        
        # Filter based on role permissions
        if user.role == 'SUPER_ADMIN':
            # Super Admin can see all pending users EXCEPT Students
            return queryset.exclude(role='STUDENT')
        elif user.role == 'ADMIN':
            # Admin can ONLY see Students
            return queryset.filter(role='STUDENT')
        elif user.role == 'HOD':
            # HOD can see Faculty and Students in their department
            dept = user.departments_headed.first() or user.department_fk
            if dept:
                return queryset.filter(role__in=['FACULTY', 'STUDENT'], department_fk=dept)
            return User.objects.none()
        
        return User.objects.none()

@require_POST
def approve_user(request, pk):
    """Approve or reject a user account"""
    if not request.user.can_approve_users():
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')
    
    user_to_approve = get_object_or_404(User, pk=pk)
    action = request.POST.get('action')
    
    # Check if current user has permission to approve this user
    if request.user.role == 'HOD':
        # HOD can only approve Faculty/Students in their department
        dept = request.user.departments_headed.first() or request.user.department_fk
        if user_to_approve.role not in ['FACULTY', 'STUDENT'] or user_to_approve.department_fk != dept:
            messages.error(request, "You can only approve members in your department.")
            return redirect('user_approval')
    elif request.user.role == 'SUPER_ADMIN':
        # Super Admin can approve all users EXCEPT Students
        if user_to_approve.role == 'STUDENT':
            messages.error(request, "Super Admin cannot approve students. This must be done by an Admin.")
            return redirect('user_approval')
    elif request.user.role == 'ADMIN':
        # Admin can ONLY approve Students
        if user_to_approve.role != 'STUDENT':
            messages.error(request, "Admins can only approve student accounts. Other roles must be approved by Super Admin.")
            return redirect('user_approval')
    
    if action == 'approve':
        user_to_approve.is_approved = True
        user_to_approve.is_active = True
        user_to_approve.approved_by = request.user
        user_to_approve.approved_at = timezone.now()
        user_to_approve.save()
        
        # Send email notification
        send_approval_email(user_to_approve, approved=True)
        
        messages.success(request, f"Approved user account: {user_to_approve.username}")
    elif action == 'reject':
        # Send rejection email before deletion
        send_approval_email(user_to_approve, approved=False)
        user_to_approve.delete()
        messages.success(request, f"Rejected (deleted) user account: {user_to_approve.username}")
        
    return redirect('user_approval')

# Keep old view for backward compatibility
class StudentApprovalListView(UserApprovalListView):
    """Legacy view - redirects to new user approval"""
    def get_queryset(self):
        return User.objects.filter(role='STUDENT', is_active=False, is_approved=False).order_by('-date_joined')

@require_POST
def approve_student(request, pk):
    """Legacy function - redirects to new approve_user"""
    return approve_user(request, pk)

class FacultyListView(LoginRequiredMixin, HODRequiredMixin, ListView):
    model = User
    template_name = 'users/faculty_list.html'
    context_object_name = 'faculty_members'
    
    def get_queryset(self):
        queryset = User.objects.filter(role='FACULTY')
        # HOD can only see faculty in their department
        dept = self.request.user.departments_headed.first() or self.request.user.department_fk
        if self.request.user.role == 'HOD' and dept:
            queryset = queryset.filter(department_fk=dept)
        return queryset

class FacultyCreateView(LoginRequiredMixin, HODRequiredMixin, CreateView):
    model = User
    form_class = FacultyCreationForm
    template_name = 'users/faculty_form.html'
    success_url = reverse_lazy('faculty_list')

    def form_valid(self, form):
        form.instance.role = 'FACULTY'
        form.instance.is_approved = True  # Auto-approve if created by admin
        form.instance.is_active = True
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        messages.success(self.request, "Faculty member added successfully!")
        return super().form_valid(form)

class AdminStudentCreateView(LoginRequiredMixin, HODRequiredMixin, CreateView):
    """Admin can create Student accounts directly"""
    model = User
    form_class = AdminStudentCreationForm
    template_name = 'users/admin_student_create.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        # Form already handles password hashing in its save() method
        user.role = 'STUDENT'
        user.is_approved = True
        user.is_active = True
        user.approved_by = self.request.user
        user.approved_at = timezone.now()
        user.save()
        messages.success(self.request, f"Student account '{user.username}' created successfully!")
        return redirect(self.success_url)
