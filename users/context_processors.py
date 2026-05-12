from .models import User

def pending_approvals_count(request):
    """
    Context processor to provide the count of pending user approvals.
    """
    if request.user.is_authenticated:
        user = request.user
        queryset = User.objects.filter(is_approved=False, is_active=False)
        
        if user.role == 'SUPER_ADMIN':
            return {'pending_approvals_count': queryset.count()}
        elif user.role == 'ADMIN':
            # Admin can see and approve Students, Placement Officers, Faculty
            return {'pending_approvals_count': queryset.filter(role__in=['STUDENT', 'PLACEMENT_OFFICER', 'FACULTY']).count()}
        elif user.role == 'HOD':
            # HOD can only see Faculty in their department
            if user.department_fk:
                return {'pending_approvals_count': queryset.filter(role='FACULTY', department_fk=user.department_fk).count()}
    
    return {'pending_approvals_count': 0}
