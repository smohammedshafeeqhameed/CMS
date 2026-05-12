import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User
from students.models import StudentProfile, Certificate
from django.core.files.base import ContentFile
import datetime

# Create User
username = 'demo_student'
if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(username=username, email='demo@example.com', password='password123')
    user.role = 'STUDENT'
    user.save()
    print(f"Created user: {user.username} (ID: {user.pk})")
else:
    user = User.objects.get(username=username)
    print(f"Using existing user: {user.username} (ID: {user.pk})")

# Create Profile
if not hasattr(user, 'student_profile'):
    StudentProfile.objects.create(
        user=user,
        batch='Class of 2025',
        bio='Aspiring Software Engineer',
        cgpa=9.5,
        linkedin_url='https://linkedin.com/in/demo',
        github_url='https://github.com/demo'
    )
    print("Created student profile")

# Create Certificate
if not Certificate.objects.filter(student=user, name='Python Mastery').exists():
    cert = Certificate.objects.create(
        student=user,
        name='Python Mastery',
        issuing_organization='Coursera',
        issue_date=datetime.date.today(),
        is_verified=False
    )
    # create dummy file
    cert.certificate_file.save('cert.txt', ContentFile(b'dummy certificate content'))
    cert.save()
    print("Created dummy certificate")
else:
    print("Certificate already exists")
