from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PDFChatAssistantView

urlpatterns = [
    path('assistant/', csrf_exempt(PDFChatAssistantView.as_view()), name='ai_assistant'),
]
