"""
Views for certificate/badge management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Certificate
from users.mixins import StudentRequiredMixin


class CertificateCreateView(LoginRequiredMixin, StudentRequiredMixin, CreateView):
    """View for students to add new certificates"""
    model = Certificate
    fields = ['name', 'issuing_organization', 'issue_date', 'certificate_file']
    template_name = 'students/certificate_form.html'
    success_url = reverse_lazy('certificate_list')
    
    def form_valid(self, form):
        form.instance.student = self.request.user
        messages.success(self.request, "Certificate added successfully! It will be verified by faculty.")
        return super().form_valid(form)


class CertificateListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    """View for students to see their certificates"""
    model = Certificate
    template_name = 'students/certificate_list.html'
    context_object_name = 'certificates'
    
    def get_queryset(self):
        return Certificate.objects.filter(student=self.request.user).order_by('-issue_date')


class CertificateDeleteView(LoginRequiredMixin, StudentRequiredMixin, DeleteView):
    """View for students to delete their certificates"""
    model = Certificate
    template_name = 'students/certificate_confirm_delete.html'
    success_url = reverse_lazy('certificate_list')
    context_object_name = 'certificate'
    
    def get_queryset(self):
        # Only allow students to delete their own certificates
        return Certificate.objects.filter(student=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Certificate deleted successfully.")
        return super().delete(request, *args, **kwargs)

