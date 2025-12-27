class HostFixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'user_service' in request.META.get('HTTP_HOST', ''):
            request.META['HTTP_HOST'] = 'localhost'
        response = self.get_response(request)
        return response