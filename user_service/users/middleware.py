from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.http.request import HttpRequest

# Store the original get_host method
_original_get_host = HttpRequest.get_host

def patched_get_host(self):
    """Patched get_host that allows all hosts for health endpoints"""
    if hasattr(self, 'path') and self.path == '/health/':
        # For health endpoints, return the host without validation
        return self.META.get('HTTP_HOST', '').split(':')[0]
    return _original_get_host(self)

# Monkey patch the get_host method
HttpRequest.get_host = patched_get_host

class HostFixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # For other requests, fix the host header if it contains 'user_service'
        if 'user_service' in request.META.get('HTTP_HOST', ''):
            request.META['HTTP_HOST'] = 'localhost'

        response = self.get_response(request)
        return response