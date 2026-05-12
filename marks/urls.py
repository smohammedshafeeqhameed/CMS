from django.urls import path
from .views import DownloadMarksTemplateView, UploadMarksExcelView

urlpatterns = [
    path('faculty/download-template/', DownloadMarksTemplateView.as_view(), name='download_marks_template'),
    path('faculty/upload-excel/', UploadMarksExcelView.as_view(), name='upload_marks_excel'),
]
