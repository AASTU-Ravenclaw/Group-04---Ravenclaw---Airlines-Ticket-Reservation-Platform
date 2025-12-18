from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from notifications.views import NotificationListView, NotificationDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/notifications/<str:user_id>/', NotificationListView.as_view(), name='list-notifs'),
    path('api/v1/notifications/dismiss/<str:id>/', NotificationDetailView.as_view(), name='delete-notif'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]