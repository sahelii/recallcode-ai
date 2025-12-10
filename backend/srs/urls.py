from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SRSReviewViewSet, DailyPlanViewSet

router = DefaultRouter()
router.register(r'reviews', SRSReviewViewSet, basename='srs-review')
router.register(r'plans', DailyPlanViewSet, basename='daily-plan')

urlpatterns = [
    path('', include(router.urls)),
]

