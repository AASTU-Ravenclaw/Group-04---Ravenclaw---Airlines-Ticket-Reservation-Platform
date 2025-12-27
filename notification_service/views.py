from rest_framework import views, status
from rest_framework.response import Response
from .models import Notification


class NotificationListView(views.APIView):

    def get(self, request, user_id):
        notifications = (
            Notification.objects(user_id=user_id).order_by("-timestamp").limit(20)
        )
        data = [n.to_dict() for n in notifications]
        return Response(data, status=status.HTTP_200_OK)


class NotificationDetailView(views.APIView):

    def delete(self, request, id):
        try:
            Notification.objects.get(id=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
