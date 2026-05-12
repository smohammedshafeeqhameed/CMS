from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, SignUpView, DashboardView, 
    UserApprovalListView, approve_user,
    StudentApprovalListView, approve_student,  # Legacy views
    FacultyCreateView, FacultyListView, AdminStudentCreateView
)
from .password_reset_views import (
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)
from .super_admin_views import (
    AdminListView, AdminCreateView,
    HODListView, HODCreateView,
    SuperAdminFacultyCreateView,
    SuperAdminDepartmentCreateView, SuperAdminDepartmentListView,
    SuperAdminDepartmentUpdateView, SuperAdminDepartmentDeleteView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Password reset
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # User approval (new unified view)
    path('user-approval/', UserApprovalListView.as_view(), name='user_approval'),
    path('user-approval/<int:pk>/', approve_user, name='approve_user'),
    
    # Legacy student approval (for backward compatibility)
    path('student-approval/', StudentApprovalListView.as_view(), name='student_approval'),
    path('student-approval/<int:pk>/', approve_student, name='approve_student'),
    
    # Faculty management
    path('faculty/', FacultyListView.as_view(), name='faculty_list'),
    path('faculty/add/', FacultyCreateView.as_view(), name='add_faculty'),
    path('student/add/', AdminStudentCreateView.as_view(), name='admin_student_create'),
    
    # Super Admin - Admin Management
    path('super-admin/admins/', AdminListView.as_view(), name='admin_list'),
    path('super-admin/admins/add/', AdminCreateView.as_view(), name='admin_create'),
    
    # Super Admin - HOD Management
    path('super-admin/hods/', HODListView.as_view(), name='hod_list'),
    path('super-admin/hods/add/', HODCreateView.as_view(), name='hod_create'),
    
    # Super Admin - Faculty Management
    path('super-admin/faculty/add/', SuperAdminFacultyCreateView.as_view(), name='super_admin_faculty_create'),
    
    # Super Admin - Department Management
    path('super-admin/departments/', SuperAdminDepartmentListView.as_view(), name='super_admin_department_list'),
    path('super-admin/departments/add/', SuperAdminDepartmentCreateView.as_view(), name='super_admin_department_create'),
    path('super-admin/departments/<int:pk>/edit/', SuperAdminDepartmentUpdateView.as_view(), name='super_admin_department_edit'),
    path('super-admin/departments/<int:pk>/delete/', SuperAdminDepartmentDeleteView.as_view(), name='super_admin_department_delete'),
]
