from django.urls import path
from .views import chat_with_coach

urlpatterns = [
    path('chat/', chat_with_coach, name='chat-with-coach'),
]

