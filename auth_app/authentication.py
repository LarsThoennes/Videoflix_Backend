from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication using cookies.

    This authentication class handles:
    - retrieving the JWT access token from HTTP cookies
    - validating the token using SimpleJWT
    - authenticating the corresponding user
    - returning None if the token is missing or invalid
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            return None