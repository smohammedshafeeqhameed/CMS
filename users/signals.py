from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from students.models import StudentProfile

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'STUDENT':
        StudentProfile.objects.create(user=instance)
