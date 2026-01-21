from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Notification


class TraefikAuthPermission(BasePermission):
    """
    Custom permission to check X-User-Id header set by Traefik auth middleware
    """
    def has_permission(self, request, view):
        user_id = request.META.get('HTTP_X_USER_ID')
        if not user_id:
            return False
        # Store user_id in request for use in views
        request.user_id = user_id
        return True


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(views.APIView):
    permission_classes = [TraefikAuthPermission]

    @swagger_auto_schema(
        operation_description="Get user notifications",
        operation_summary="List notifications for a user",
        responses={
            200: openapi.Response(
                description="List of notifications",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                                    'event_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            403: "Unauthorized"
        }
    )
    def get(self, request, user_id):
        # Ensure user can only access their own notifications
        if request.user_id != user_id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        notifications = Notification.objects(user_id=user_id).order_by("-timestamp")
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(notifications, request)
        data = [n.to_dict() for n in page]
        return paginator.get_paginated_response(data)


class NotificationUnreadCountView(views.APIView):
    permission_classes = [TraefikAuthPermission]

    @swagger_auto_schema(
        operation_description="Get unread notification count for a user",
        operation_summary="Get count of unread notifications",
        responses={
            200: openapi.Response(
                description="Unread count",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'unread_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            403: "Unauthorized"
        }
    )
    def get(self, request, user_id):
        # Ensure user can only access their own notifications
        if request.user_id != user_id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        unread_count = Notification.objects(user_id=user_id, is_read=False).count()
        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)


class NotificationDetailView(views.APIView):
    permission_classes = [TraefikAuthPermission]

    @swagger_auto_schema(
        operation_description="Mark a notification as read",
        operation_summary="Mark notification as read",
        responses={
            200: openapi.Response(
                description="Notification marked as read",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'event_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            403: "Unauthorized",
            404: "Not found"
        }
    )
    def patch(self, request, id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(id=id)
            # Ensure user can only modify their own notifications
            if request.user_id != notification.user_id:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            notification.is_read = True
            notification.save()
            return Response(notification.to_dict(), status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
