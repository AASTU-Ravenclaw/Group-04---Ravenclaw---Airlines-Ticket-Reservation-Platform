import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

class RemoteUser:
    """
    A temporary user object since we don't store users in this DB.
    """
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role
        self.is_authenticated = True

    def __str__(self):
        return self.email

class RemoteJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None 

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            user_id = payload.get('user_id')
            email = payload.get('email', '')
            role = payload.get('role', 'CLIENT')

            user = RemoteUser(user_id, email, role)
            
            return (user, token)

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
            return None