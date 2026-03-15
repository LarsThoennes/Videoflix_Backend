from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from .serializers import RegistrationSerializer, CustomTokenObtainSerializer, PasswordConfirmSerializer
from ..services.email_service import send_reset_password_email

        
class RegistrationView(APIView):
    """
    API endpoint for user registration.

    This view handles:
    - validating incoming registration data
    - creating a new user account
    - marking the account as inactive until email confirmation
    - returning basic user information after successful registration
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic(): 
                saved_account = serializer.save()
                saved_account.is_active = False
                saved_account.save()

            return Response(
                {
                    "user": {
                        "id": saved_account.pk,
                        "email": saved_account.email,
                    },
                    "token": "auth_token",
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    """
    API endpoint for activating user accounts.

    This view handles:
    - decoding the user ID from the activation URL
    - validating the activation token
    - activating the user account
    - returning appropriate success or error responses
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):

                if user.is_active:
                    return Response(
                        {"message": "This link has expired."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.is_active = True
                user.save()

                return Response(
                    {"message": "Account successfully activated."},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Activation failed."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(TokenObtainPairView):
    """
    API endpoint for user authentication.

    This view handles:
    - validating user login credentials
    - generating JWT access and refresh tokens
    - storing the tokens securely in HTTP-only cookies
    - returning basic user information after successful login
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        user = serializer.user 

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                }
            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=False,
            samesite='Lax',
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
        )

        csrf_token = get_token(request)

        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            httponly=False,
            secure=False,
            samesite="Lax",
        )

        return response
    
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass

        response = Response(
            {"detail": "Logout successful!"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        response.delete_cookie("csrftoken", path="/")

        return response
    
class TokenRefreshView(TokenRefreshView):
    """
    API endpoint for refreshing JWT access tokens.

    This view handles:
    - retrieving the refresh token from cookies
    - validating the refresh token
    - generating a new access token
    - updating the access token cookie
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'error': 'No refresh token provided in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'error': 'Refresh Token invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get('access')

        response = Response({'detail': 'Token refreshed', 'access': access_token}, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
        )

        return response
    
class PasswordResetView(APIView):
    """
    API endpoint for requesting a password reset.

    This view handles:
    - receiving the user's email address
    - checking if an account exists for the email
    - generating a secure reset token and encoded user ID
    - sending a password reset email if the user exists
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)

            if user.is_active:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                send_reset_password_email(user, token, uidb64)

        except User.DoesNotExist:
            pass 

        return Response(
            {"detail": "If an account with this email exists, a password reset email has been sent."},
            status=status.HTTP_200_OK
        )
    
class PasswordConfirmView(APIView):
    """
    API endpoint for confirming and setting a new password.

    This view handles:
    - decoding the user ID from the reset URL
    - validating the password reset token
    - validating the new password using a serializer
    - updating the user's password
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not user.is_active:
                return Response(
                    {"error": "User is not active."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = PasswordConfirmSerializer(
                instance=user,
                data=request.data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"detail": "Your password has been successfully reset."},
                status=status.HTTP_200_OK
            )

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Password Confirmation failed."},
                status=status.HTTP_400_BAD_REQUEST
            )