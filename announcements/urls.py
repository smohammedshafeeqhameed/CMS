from django.urls import path
from .views import AnnouncementListView, AnnouncementCreateView, AnnouncementDetailView

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    path('add/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
]
