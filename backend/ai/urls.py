from django.urls import path
from .views import generate_hint

urlpatterns = [
    path('hint/', generate_hint, name='generate-hint'),
]

