import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

class RemoteUser:
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role
        self.is_authenticated = True

    def __str__(self):
        return self.email

class HeaderAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user_id = request.META.get('HTTP_X_USER_ID')

        if not user_id:
            return None

        email = request.META.get('HTTP_X_USER_EMAIL', '')
        role = request.META.get('HTTP_X_USER_ROLE', 'CLIENT')

        user = RemoteUser(user_id, email, role)
        
        return (user, None)