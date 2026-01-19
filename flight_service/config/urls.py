from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from flights.views import LocationViewSet, FlightViewSet

def health_check(request):
    return JsonResponse({'status': 'healthy'})

# Import drf-yasg schema generator
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. Define the Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Flight Service API",
      default_version='v1',
      description="API for managing locations and flights",
      # terms_of_service="https://www.google.com/policies/terms/", # Optional
      # contact=openapi.Contact(email="contact@flights.local"), # Optional
      # license=openapi.License(name="BSD License"), # Optional
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

# Initialize the router for viewsets
router = DefaultRouter()
# Register your viewsets
router.register(r'locations', LocationViewSet)
router.register(r'flights', FlightViewSet)

urlpatterns = [
    # 1. Django Admin
    path('admin/', admin.site.urls),
    
    # 2. API Routes (using the router)
    path('api/v1/', include(router.urls)),
    
    # Health Check
    path('health/', health_check, name='health_check'),
    
    # --- DRF-YASG DOCUMENTATION ENDPOINTS ---
    
    # 3. Schema Generation: Generates the OpenAPI JSON file
    re_path(r'^api/schema/$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # 4. Swagger UI: Serves the web interface 
    re_path(r'^api/docs/swagger-ui/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    
    # 5. Redoc UI
    re_path(r'^api/docs/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
