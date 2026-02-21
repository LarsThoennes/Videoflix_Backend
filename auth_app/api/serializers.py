from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
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

    def validate_repeated_password(self, value):
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