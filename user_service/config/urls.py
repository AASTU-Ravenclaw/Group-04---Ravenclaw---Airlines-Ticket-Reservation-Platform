from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.http import JsonResponse, HttpResponse

def health_check(request):
    # Simple health check that bypasses ALLOWED_HOSTS validation
    response = HttpResponse('{"status": "healthy"}', content_type='application/json')
    return response

# Swagger Configuration
schema_view = get_schema_view(
   openapi.Info(
      title="User Service API",
      default_version='v1',
      description="API for Authentication and User Management",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('health/', health_check, name='health_check'),
    path('', include('django_prometheus.urls')),
    
    # Swagger Documentation URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]