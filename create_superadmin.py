"""
Script to create a Super Admin user for the CMS
Run this script using: python manage.py shell < create_superadmin.py
Or run: python manage.py shell and paste the code
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User
from django.utils import timezone

def create_superadmin():
    """Create a Super Admin user"""
    username = 'superadmin'
    email = 'superadmin@college.edu'
    password = 'superadmin123'  # Change this password after first login!
    
    # Check if superadmin already exists
    if User.objects.filter(username=username).exists():
        print(f"Super Admin user '{username}' already exists!")
        user = User.objects.get(username=username)
        print(f"Current role: {user.role}")
        print(f"Is active: {user.is_active}")
        print(f"Is approved: {user.is_approved}")
        return user
    
    # Create Super Admin user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='SUPER_ADMIN',
        is_staff=True,
        is_superuser=True,  # Django superuser for admin panel access
        is_active=True,
        is_approved=True,  # Auto-approve Super Admin
        approved_at=timezone.now()
    )
    
    print("=" * 60)
    print("Super Admin Account Created Successfully!")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Role: {user.get_role_display()}")
    print("=" * 60)
    print("\nIMPORTANT: Change the password after first login!")
    print("=" * 60)
    
    return user

if __name__ == '__main__':
    create_superadmin()

