"""
Password reset views for the CMS
"""
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from .utils import send_password_reset_email


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with email notification"""
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        # Send custom email
        email = form.cleaned_data['email']
        try:
            from .models import User
            user = User.objects.get(email=email)
            # Generate reset link
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.urls import reverse
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = self.request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_password_reset_email(user, reset_link)
        except:
            pass  # User doesn't exist, but don't reveal this
        
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

