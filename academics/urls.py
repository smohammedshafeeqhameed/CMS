from django.urls import path
from .views import (
    DepartmentListView, DepartmentCreateView,
    CourseListView, CourseCreateView, CourseUpdateView,
    SubjectListView, SubjectCreateView,
    EnrollmentListView, EnrollmentCreateView,
    TimetableListView, TimetableCreateView,
    TimeSlotListView, TimeSlotCreateView,
    AcademicAdvisorListView, AcademicAdvisorCreateView,
    AcademicAdvisorUpdateView, AcademicAdvisorDeleteView,
    MaterialListView, MaterialCreateView, MaterialDeleteView,
    TimetableDocumentListView, TimetableDocumentCreateView, TimetableDocumentDeleteView,
    load_courses,
)

urlpatterns = [
    # AJAX
    path('ajax/load-courses/', load_courses, name='ajax_load_courses'),

    # Departments
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', DepartmentCreateView.as_view(), name='department_create'),
    
    # Courses
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/add/', CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_edit'),
    
    # Subjects
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', SubjectCreateView.as_view(), name='subject_create'),
    
    # Enrollments
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/add/', EnrollmentCreateView.as_view(), name='enrollment_create'),
    
    # Timetable
    path('timetable/', TimetableListView.as_view(), name='timetable_list'),
    path('timetable/add/', TimetableCreateView.as_view(), name='timetable_create'),
    
    # Time Slots
    path('timeslots/', TimeSlotListView.as_view(), name='timeslot_list'),
    path('timeslots/add/', TimeSlotCreateView.as_view(), name='timeslot_create'),

    # Academic Advisor / Class Mentor Mapping
    path('advisor/', AcademicAdvisorListView.as_view(), name='advisor_list'),
    path('advisor/add/', AcademicAdvisorCreateView.as_view(), name='advisor_create'),
    path('advisor/<int:pk>/edit/', AcademicAdvisorUpdateView.as_view(), name='advisor_edit'),
    path('advisor/<int:pk>/delete/', AcademicAdvisorDeleteView.as_view(), name='advisor_delete'),

    # Study Materials
    path('materials/', MaterialListView.as_view(), name='material_list'),
    path('materials/add/', MaterialCreateView.as_view(), name='material_create'),
    path('materials/<int:pk>/delete/', MaterialDeleteView.as_view(), name='material_delete'),
    # Timetable Documents (File-based)
    path('timetable-docs/', TimetableDocumentListView.as_view(), name='timetable_doc_list'),
    path('timetable-docs/add/', TimetableDocumentCreateView.as_view(), name='timetable_doc_create'),
    path('timetable-docs/<int:pk>/delete/', TimetableDocumentDeleteView.as_view(), name='timetable_doc_delete'),
]

