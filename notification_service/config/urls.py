from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from notifications.views import NotificationListView, NotificationDetailView, NotificationUnreadCountView, health_check

# Define the Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Notification Service API",
      default_version='v1',
      description="API for managing user notifications",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/notifications/<str:user_id>/', NotificationListView.as_view(), name='list-notifs'),
    path('api/v1/notifications/<str:user_id>/unread-count/', NotificationUnreadCountView.as_view(), name='unread-count'),
    path('api/v1/notifications/<str:id>/read/', NotificationDetailView.as_view(), name='mark-read-notif'),
    
    # Health Check
    path('health/', health_check, name='health_check'),
    path('', include('django_prometheus.urls')),
    
    # DRF-YASG DOCUMENTATION ENDPOINTS
    re_path(r'^api/schema/notification/$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/docs/notification/swagger-ui/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)