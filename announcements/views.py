from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Announcement, AnnouncementCategory
from django.db.models import Q
from users.mixins import AdminOrHODRequiredMixin

class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin or user.is_admin:
            return Announcement.objects.all().order_by('-posted_at')
        
        # Filtering for Student/Faculty/HOD
        # 1. Global announcements (ALL)
        # 2. Targeted by role (STUDENTS/FACULTY)
        # 3. Targeted by department (if applicable)
        # 4. Individuals (INDIVIDUAL)
        
        q_filter = Q(target_audience='ALL')
        
        if user.is_student:
            q_filter |= Q(target_audience='STUDENTS')
            if hasattr(user, 'student_profile') and user.student_profile.course:
                q_filter |= Q(target_audience='DEPARTMENT', target_department=user.student_profile.course.department)
                if user.student_profile.batch:
                    q_filter |= Q(target_audience='BATCH', target_batch=user.student_profile.batch)
        
        if user.is_faculty or user.is_hod:
            q_filter |= Q(target_audience='FACULTY')
            if user.department_fk:
                q_filter |= Q(target_audience='DEPARTMENT', target_department=user.department_fk)
        
        q_filter |= Q(target_audience='INDIVIDUAL', target_individual=user)
        
        return Announcement.objects.filter(q_filter, is_active=True).order_by('-is_pinned', '-posted_at')

class AnnouncementCreateView(LoginRequiredMixin, AdminOrHODRequiredMixin, CreateView):
    model = Announcement
    fields = ['title', 'content', 'category', 'priority', 'target_audience', 'target_department', 'target_batch', 'expiry_date', 'attachment', 'is_pinned']
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')
    
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_hod and user.department_fk:
            initial['target_department'] = user.department_fk
            initial['target_audience'] = 'DEPARTMENT'
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Add Tailwind classes to form fields since @apply might not work in template
        for field_name, field in form.fields.items():
            if field_name == 'is_pinned':
                field.widget.attrs.update({'class': 'w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary'})
            else:
                field.widget.attrs.update({'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all'})

        # HODs should ideally only post to their department
        if user.is_hod and not user.is_super_admin:
            from academics.models import Department
            form.fields['target_department'].queryset = Department.objects.filter(id=user.department_fk.id) if user.department_fk else Department.objects.none()
            
        return form
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, "Announcement published successfully!")
        return super().form_valid(form)

class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'
