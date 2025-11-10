# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # Register user
    path('login/', LoginView.as_view(), name='login'),  # Login user
    path('profile/', ProfileView.as_view(), name='profile'),  # Get user profile
]
