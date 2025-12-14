from django.urls import path

from .views import ChatbotView, ChatbotHealthView, ChatbotInfoView

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot endpoint
    path('chat/', ChatbotView.as_view(), name='chat'),

    # Health check endpoint
    path('health/', ChatbotHealthView.as_view(), name='health'),

    # Information endpoint
    path('info/', ChatbotInfoView.as_view(), name='info'),
]
