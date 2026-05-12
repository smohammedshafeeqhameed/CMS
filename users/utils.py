"""
Utility functions for user management
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_approval_email(user, approved=True):
    """
    Send email notification to user about approval status
    
    Args:
        user: User instance
        approved: Boolean indicating if user was approved or rejected
    """
    if not settings.EMAIL_HOST_USER:
        # Email not configured, skip sending
        return
    
    try:
        if approved:
            subject = 'Account Approved - College Management System'
            message = f"""
            Dear {user.get_full_name() or user.username},
            
            Your account has been approved. You can now log in to the College Management System.
            
            Username: {user.username}
            
            Please log in at: {settings.LOGIN_URL}
            
            Best regards,
            College Management System
            """
        else:
            subject = 'Account Rejection - College Management System'
            message = f"""
            Dear {user.get_full_name() or user.username},
            
            We regret to inform you that your account registration has been rejected.
            
            If you believe this is an error, please contact the administration.
            
            Best regards,
            College Management System
            """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,  # Don't raise exception if email fails
        )
    except Exception as e:
        # Log error but don't break the approval process
        print(f"Error sending approval email: {e}")


def send_password_reset_email(user, reset_link):
    """
    Send password reset email to user
    
    Args:
        user: User instance
        reset_link: Password reset URL
    """
    if not settings.EMAIL_HOST_USER:
        return
    
    try:
        subject = 'Password Reset Request - College Management System'
        message = f"""
        Dear {user.get_full_name() or user.username},
        
        You have requested to reset your password. Click the link below to reset it:
        
        {reset_link}
        
        If you did not request this, please ignore this email.
        
        Best regards,
        College Management System
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending password reset email: {e}")

