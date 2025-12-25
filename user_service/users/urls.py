from django.urls import path
from .views import RegisterView, CustomLoginView, CustomRefreshView, UserProfileView

urlpatterns = [
    # Auth Endpoints
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', CustomLoginView.as_view(), name='login'),
    path('auth/refresh', CustomRefreshView.as_view(), name='token_refresh'),
    
    # Profile Endpoint
    # Using 'me' instead of ID since the token already identifies the user
    path('users/me', UserProfileView.as_view(), name='profile'),
]