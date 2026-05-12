from django.urls import path
from . import views

urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='assignment_list'),
    path('add/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('<int:pk>/submit/', views.AssignmentSubmissionView.as_view(), name='assignment_submit'),
    path('<int:pk>/submissions/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submission/<int:pk>/grade/', views.GradeSubmissionView.as_view(), name='grade_submission'),
]
