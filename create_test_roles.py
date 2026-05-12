
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User

def create_user(username, password, role):
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password, role=role)
        print(f"Created {role} user: {username}")
    else:
        print(f"User {username} already exists")

create_user('testfaculty', 'testpassword123', 'FACULTY')
create_user('testindustry', 'testpassword123', 'INDUSTRY')
create_user('testemployer', 'testpassword123', 'EMPLOYER')
create_user('testplacement', 'testpassword123', 'PLACEMENT_CELL')
