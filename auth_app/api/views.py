from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer
from ..services.email_service import send_activation_email
from ..models import UserProfile

        
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic(): 
                saved_account = serializer.save()

                UserProfile.objects.create(
                    user=saved_account,
                    is_active=False
                )

                uidb64 = urlsafe_base64_encode(force_bytes(saved_account.pk))
                token = default_token_generator.make_token(saved_account)

                send_activation_email(saved_account, token, uidb64)

            return Response(
                {
                    "user": {
                        "id": saved_account.pk,
                        "email": saved_account.email,
                    },
                    "token": token,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):

                profile = UserProfile.objects.get(user=user)

                if profile.is_active == True:
                    return Response(
                    {"message": "Dieser Link wurde bereits verwendet. Ihr Konto ist aktiviert."},
                    status=status.HTTP_400_BAD_REQUEST
                )

                profile.is_active = True
                profile.save()

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
