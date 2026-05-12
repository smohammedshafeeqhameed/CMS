"""
Management command style script to create Super Admin
Run: python manage.py shell
Then copy and paste the code below
"""
from users.models import User
from django.utils import timezone

username = 'superadmin'
email = 'superadmin@college.edu'
password = 'superadmin123'  # Change this after first login!

# Check if superadmin already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"Super Admin user '{username}' already exists!")
    print(f"Current role: {user.role}")
    print(f"Is active: {user.is_active}")
    print(f"Is approved: {user.is_approved}")
    if user.role != 'SUPER_ADMIN':
        user.role = 'SUPER_ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_approved = True
        user.save()
        print(f"Updated user '{username}' to SUPER_ADMIN role!")
else:
    # Create Super Admin user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='SUPER_ADMIN',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_approved=True,
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
    print("\n⚠️  IMPORTANT: Change the password after first login!")
    print("=" * 60)

