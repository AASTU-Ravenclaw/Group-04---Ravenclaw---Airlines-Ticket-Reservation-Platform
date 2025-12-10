import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import datetime

from .models import Booking
from .serializers import BookingSerializer
from .producer import publish_event


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        flight_id = serializer.validated_data['flight_id']
        seats_needed = serializer.validated_data['passengers']
        
        flight_url = f"{settings.FLIGHT_SERVICE_URL}/{flight_id}/reserve_seat/"

        headers = {'X-Service-API-Key': settings.SERVICE_API_KEY}
        for _ in range(seats_needed):
            response = requests.post(flight_url, headers=headers)
            if response.status_code != 200:
                return Response(
                    {"error": f"Failed to reserve seat. Status: {response.status_code}, Response: {response.text}"}, 
                    status=status.HTTP_409_CONFLICT
                )

        serializer.validated_data['user_id'] = request.user.id
        booking = serializer.save()

        event_data = {
            "booking_id": str(booking.booking_id),
            "user_id": str(booking.user_id),
            "email": getattr(request.user, 'email', 'N/A'), 
            "flight_id": str(booking.flight_id),
            "status": "CONFIRMED",
            "timestamp": datetime.datetime.now().isoformat()
        }
        publish_event('booking_created', event_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):

        try:
            booking = self.get_object()
            
            if booking.status == 'CANCELLED':
                return Response({"message": "Already cancelled"}, status=status.HTTP_400_BAD_REQUEST)


            seats_to_release = booking.passengers.count() or 1
            
            flight_url = f"{settings.FLIGHT_SERVICE_URL}/{booking.flight_id}/release_seat/"
            
            headers = {'X-Service-API-Key': settings.SERVICE_API_KEY}
            for _ in range(seats_to_release):
                requests.post(flight_url, headers=headers)

            booking.status = 'CANCELLED'
            booking.save()

            event_data = {
                "booking_id": str(booking.booking_id),
                "user_id": str(booking.user_id),
                "email": getattr(request.user, 'email', 'N/A'),
                "flight_id": str(booking.flight_id),
                "status": "CANCELLED",
                "timestamp": datetime.datetime.now().isoformat()
            }
            publish_event('booking_cancelled', event_data)

            return Response({"status": "Booking cancelled successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)