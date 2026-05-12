from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import LandingPageView, CollegeChatbotView

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('chatbot/', csrf_exempt(CollegeChatbotView.as_view()), name='college_chatbot'),
]
