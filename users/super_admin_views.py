"""
Views for Super Admin to manage Admin, HOD, Faculty accounts and Departments
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import User
from .forms import AdminCreationForm, HODCreationForm, FacultyCreationForm
from .mixins import SuperAdminRequiredMixin
from academics.models import Department
from django.core.exceptions import PermissionDenied


# Admin Management Views
class AdminListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    """List all Admin accounts"""
    model = User
    template_name = 'users/super_admin/admin_list.html'
    context_object_name = 'admins'
    
    def get_queryset(self):
        return User.objects.filter(role='ADMIN').order_by('username')


class AdminCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    """Create new Admin account"""
    model = User
    form_class = AdminCreationForm
    template_name = 'users/super_admin/admin_form.html'
    success_url = reverse_lazy('admin_list')
    
    def form_valid(self, form):
        form.instance.role = 'ADMIN'
        form.instance.is_approved = True  # Auto-approve if created by Super Admin
        form.instance.is_active = True
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        messages.success(self.request, f"Admin account '{form.instance.username}' created successfully!")
        return super().form_valid(form)


# HOD Management Views
class HODListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    """List all HOD accounts"""
    model = User
    template_name = 'users/super_admin/hod_list.html'
    context_object_name = 'hods'
    
    def get_queryset(self):
        return User.objects.filter(role='HOD').select_related('department_fk').order_by('username')


class HODCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    """Create new HOD account"""
    model = User
    form_class = HODCreationForm
    template_name = 'users/super_admin/hod_form.html'
    success_url = reverse_lazy('hod_list')
    
    def form_valid(self, form):
        form.instance.role = 'HOD'
        form.instance.is_approved = True  # Auto-approve if created by Super Admin
        form.instance.is_active = True
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        
        # Update department HOD if department is selected
        department = form.instance.department_fk
        if department:
            department.hod = form.instance
            department.save()
        
        messages.success(self.request, f"HOD account '{form.instance.username}' created successfully!")
        return super().form_valid(form)


# Faculty Management for Super Admin
class SuperAdminFacultyCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    """Super Admin can create Faculty accounts"""
    model = User
    form_class = FacultyCreationForm
    template_name = 'users/super_admin/faculty_form.html'
    success_url = reverse_lazy('faculty_list')
    
    def form_valid(self, form):
        form.instance.role = 'FACULTY'
        form.instance.is_approved = True
        form.instance.is_active = True
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        messages.success(self.request, f"Faculty account '{form.instance.username}' created successfully!")
        return super().form_valid(form)


# Department Management for Super Admin
class SuperAdminDepartmentCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    """Super Admin can create departments"""
    model = Department
    fields = ['name', 'code', 'hod', 'description', 'is_active']
    template_name = 'users/super_admin/department_form.html'
    success_url = reverse_lazy('super_admin_department_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Department '{form.instance.name}' created successfully!")
        return super().form_valid(form)


class SuperAdminDepartmentListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    """Super Admin can view all departments"""
    model = Department
    template_name = 'users/super_admin/department_list.html'
    context_object_name = 'departments'
    
    def get_queryset(self):
        return Department.objects.all().order_by('name')


class SuperAdminDepartmentUpdateView(LoginRequiredMixin, SuperAdminRequiredMixin, UpdateView):
    """Super Admin can update departments"""
    model = Department
    fields = ['name', 'code', 'hod', 'description', 'is_active']
    template_name = 'users/super_admin/department_form.html'
    success_url = reverse_lazy('super_admin_department_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Department '{form.instance.name}' updated successfully!")
        return super().form_valid(form)


class SuperAdminDepartmentDeleteView(LoginRequiredMixin, SuperAdminRequiredMixin, DeleteView):
    """Super Admin can delete departments"""
    model = Department
    template_name = 'users/super_admin/department_confirm_delete.html'
    success_url = reverse_lazy('super_admin_department_list')
    context_object_name = 'department'
    
    def delete(self, request, *args, **kwargs):
        department = self.get_object()
        messages.success(request, f"Department '{department.name}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

