"""
Permission mixins for role-based access control
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class SuperAdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require Super Admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'SUPER_ADMIN'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Super Admin to access this page.")
        return redirect('login')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require Admin or Super Admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['SUPER_ADMIN', 'ADMIN']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be an Admin or Super Admin to access this page.")
        return redirect('login')


class HODRequiredMixin(UserPassesTestMixin):
    """Mixin to require HOD, Admin, or Super Admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['SUPER_ADMIN', 'ADMIN', 'HOD']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Head of Department, Admin, or Super Admin to access this page.")
        return redirect('login')


class FacultyRequiredMixin(UserPassesTestMixin):
    """Mixin to require Faculty role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'FACULTY'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Faculty member to access this page.")
        return redirect('login')


class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin to require Student role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'STUDENT'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Student to access this page.")
        return redirect('login')


class PlacementOfficerRequiredMixin(UserPassesTestMixin):
    """Mixin to require Placement Officer or Placement Cell role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['PLACEMENT_OFFICER', 'PLACEMENT_CELL']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Placement Officer to access this page.")
        return redirect('login')


class AdminOrHODRequiredMixin(UserPassesTestMixin):
    """Mixin to require Admin, HOD, or Super Admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['SUPER_ADMIN', 'ADMIN', 'HOD']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be an Admin, HOD, or Super Admin to access this page.")
        return redirect('login')


class LibraryStaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require Librarian, Admin, or Super Admin role"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['SUPER_ADMIN', 'ADMIN', 'LIBRARIAN']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a Librarian or Admin to access this page.")
        return redirect('login')

