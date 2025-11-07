"""
Custom JWT authentication using httpOnly cookies for better security
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom authentication class that reads JWT from httpOnly cookies
    instead of Authorization header
    """
    
    def authenticate(self, request):
        # Try to get token from cookie first
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT_COOKIE_NAME)
        
        # If no cookie, fall back to header (for backwards compatibility during migration)
        if raw_token is None:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
        
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
