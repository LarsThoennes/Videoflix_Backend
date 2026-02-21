from django.urls import path
from .views import RegistrationView, ActivateUserView, LoginView, LogoutView, TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('password_rest/', RegisterView.as_view(), name='register'),
    # path('password_confirm/<uidb64>/<token>/', RegisterView.as_view(), name='password_confirm'),
]