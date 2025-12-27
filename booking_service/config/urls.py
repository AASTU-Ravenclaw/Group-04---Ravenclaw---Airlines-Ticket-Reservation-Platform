from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from bookings.views import BookingViewSet

# 🌟 NEW IMPORTS for drf-yasg
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. Define the Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Booking Service API",
      default_version='v1',
      description="API for managing flight reservations",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    
    # 🌟 DRF-YASG DOCUMENTATION ENDPOINTS
    # Swagger UI
    re_path(r'^api/docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    # Schema JSON
    re_path(r'^api/schema/$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]