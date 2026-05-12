import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduCareer_Connect.settings')
django.setup()

from users.models import User
from academics.models import Enrollment, Course

print(f"Total Users: {User.objects.count()}")
print(f"Students: {User.objects.filter(role='STUDENT').count()}")
print(f"Enrollments: {Enrollment.objects.count()}")

if Enrollment.objects.exists():
    e = Enrollment.objects.first()
    print(f"Sample Enrollment: Student={e.student.username}, Course={e.course.name}, Sem={e.current_semester}")

    # Check if a faculty is filterable by students they advise
    from academics.models import AcademicAdvisor
    if AcademicAdvisor.objects.exists():
        a = AcademicAdvisor.objects.first()
        print(f"Advisor: {a.faculty.username} for {a.course.name} Sem {a.semester}")
        
        # Test the template download query logic
        students = User.objects.filter(
            role='STUDENT',
            enrollments__course=a.course,
            enrollments__current_semester=a.semester,
            enrollments__is_active=True
        ).distinct()
        print(f"Students found with current advisor query: {students.count()}")
