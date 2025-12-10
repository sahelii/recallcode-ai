from django.urls import path
from .views import (
    RegisterView,
    login_view,
    refresh_token_view,
    me_view,
    update_profile_view,
    password_reset_request,
    password_reset_confirm,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('refresh/', refresh_token_view, name='refresh-token'),
    path('me/', me_view, name='me'),
    path('me/update/', update_profile_view, name='update-profile'),
    path('password-reset/', password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
]

