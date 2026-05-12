import os
import django
from django.utils import timezone
from datetime import timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User
from placements.models import JobPosting

def create_jobs():
    # Ensure we have a placement officer user
    pc_user, _ = User.objects.get_or_create(username='placement_admin', defaults={'email': 'pc@example.com', 'role': 'PLACEMENT_CELL'})
    pc_user.set_password('admin123')
    pc_user.save()
    
    companies = ['Google', 'Microsoft', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'SpaceX', 'OpenAI']
    titles = ['Software Engineering Intern', 'Data Science Intern', 'Product Management Intern', 'UI/UX Design Intern', 'AI Research Intern']
    
    for _ in range(10):
        company = random.choice(companies)
        title = random.choice(titles)
        stipend = f"${random.randint(30, 80)}/hr"
        deadline = timezone.now() + timedelta(days=random.randint(5, 30))
        
        JobPosting.objects.create(
            title=title,
            company=company,
            description=f"Join {company} as a {title}. We are looking for passionate individuals to work on cutting-edge technology.\n\nRequirements:\n- Strong coding skills\n- Problem solving ability\n- Team player",
            department="Engineering",
            competencies="Python, Java, React, SQL",
            stipend_range=stipend,
            posted_by=pc_user,
            deadline=deadline,
            is_active=True
        )
        print(f"Created job: {title} at {company}")

if __name__ == '__main__':
    create_jobs()
