from django.urls import path
from .views import RegistrationView, ActivateUserProfileView, LoginView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateUserProfileView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
]