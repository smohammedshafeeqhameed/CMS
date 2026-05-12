from django.urls import path
from .views import (
    JobPostingListView, JobPostingCreateView, JobPostingUpdateView, JobPostingDeleteView,
    PlacementAnalyticsView, StudentListView, StudentDetailView, VerifyCertificateView,
    ApplicationListView
)

urlpatterns = [
    path('manage/', JobPostingListView.as_view(), name='manage_jobs'),
    path('create/', JobPostingCreateView.as_view(), name='create_job'),
    path('update/<int:pk>/', JobPostingUpdateView.as_view(), name='update_job'),
    path('delete/<int:pk>/', JobPostingDeleteView.as_view(), name='delete_job'),
    path('analytics/', PlacementAnalyticsView.as_view(), name='placement_analytics'),
    path('track-applications/', ApplicationListView.as_view(), name='track_applications'),
    
    # Student Management & Verification
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('verify-certificate/<int:pk>/', VerifyCertificateView.as_view(), name='verify_certificate'),
]
