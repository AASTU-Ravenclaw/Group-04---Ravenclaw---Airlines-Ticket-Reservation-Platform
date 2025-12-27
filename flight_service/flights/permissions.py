from rest_framework import permissions
from django.conf import settings

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow ADMIN users to edit objects.
    Read-only for everyone else.
    """
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', '') == 'ADMIN'
        )

class IsServiceAuthenticated(permissions.BasePermission):
    """
    Custom permission for service-to-service authentication using API key.
    """
    def has_permission(self, request, view):
        api_key = request.headers.get('X-Service-API-Key')
        return api_key == settings.SERVICE_API_KEY