from django.urls import path
from .views import FacultyAttendanceSubjectListView, MarkAttendanceView, DownloadAttendanceTemplateView, UploadAttendanceExcelView, DownloadDailyAttendanceTemplateView, UploadDailyAttendanceExcelView

urlpatterns = [
    path('faculty/subjects/', FacultyAttendanceSubjectListView.as_view(), name='faculty_attendance_subjects'),
    path('faculty/mark/<int:subject_id>/', MarkAttendanceView.as_view(), name='mark_attendance'),
    path('faculty/download-template/<int:subject_id>/', DownloadAttendanceTemplateView.as_view(), name='download_attendance_template'),
    path('faculty/download-template/', DownloadAttendanceTemplateView.as_view(), name='download_attendance_template_no_id'),
    path('faculty/upload-excel/<int:subject_id>/', UploadAttendanceExcelView.as_view(), name='upload_attendance_excel'),
    path('faculty/upload-excel/', UploadAttendanceExcelView.as_view(), name='upload_attendance_excel_no_id'),
    path('faculty/download-daily-template/<int:subject_id>/', DownloadDailyAttendanceTemplateView.as_view(), name='download_daily_template'),
    path('faculty/download-daily-template/', DownloadDailyAttendanceTemplateView.as_view(), name='download_daily_template_no_id'),
    path('faculty/upload-daily-excel/<int:subject_id>/', UploadDailyAttendanceExcelView.as_view(), name='upload_daily_excel'),
    path('faculty/upload-daily-excel/', UploadDailyAttendanceExcelView.as_view(), name='upload_daily_excel_no_id'),
]
