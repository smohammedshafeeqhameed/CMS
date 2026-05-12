import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User
from students.models import StudentProfile

def create_test_student():
    username = 'teststudent'
    password = 'testpassword123'
    email = 'student@example.com'
    
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists.")
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = 'STUDENT'
        user.save()
        print(f"User {username} created.")

    # Check if profile exists (Signal verification)
    try:
        profile = user.student_profile
        print(f"SUCCESS: StudentProfile created for {username}.")
    except StudentProfile.DoesNotExist:
        print(f"FAILURE: StudentProfile NOT created for {username}.")

if __name__ == '__main__':
    create_test_student()
