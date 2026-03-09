from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer handles:
    - validating that the email address is unique
    - validating that both password fields match
    - securely hashing the user's password
    - creating a new user account with the provided email
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        pw = self.validated_data['password']

        account = User(username=self.validated_data['email'],email=self.validated_data['email'])
        account.set_password(pw)
        account.save()
        return account

class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for JWT authentication using email.

    This serializer handles:
    - replacing the default username field with an email field
    - validating the user's email and password
    - generating JWT access and refresh tokens
    - returning authentication tokens for successful logins
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop("username", None)

        self.fields["email"] = serializers.EmailField(required=True)

    def validate(self, attrs):
       username = attrs.get("email")
       password = attrs.get("password")

       try:
           user = User.objects.get(email=username)
       except User.DoesNotExist:
           raise AuthenticationFailed("Ungültige Anmeldedaten")

       if not user.check_password(password):
           raise AuthenticationFailed("Ungültige Anmeldedaten")

       data = super().validate({
           "username": user.username,
           "password": password
       })

       return data
    
class PasswordConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming and updating a user's password.

    This serializer handles:
    - validating that the new password and confirmation match
    - applying Django's built-in password validation rules
    - securely updating the user's password
    """
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        validate_password(new_password, self.instance)

        return attrs

    def save(self):
        user = self.instance
        password = self.validated_data["new_password"]
        user.set_password(password)
        user.save()

        return user