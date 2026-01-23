import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import datetime
from opentelemetry.propagate import inject
import logging

from .models import Booking
from .serializers import BookingSerializer
from .producer import publish_event

logger = logging.getLogger(__name__)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Exclude PUT and PATCH

    def get_queryset(self):
        logger.info(
            "Incoming trace headers: traceparent=%s tracestate=%s baggage=%s",
            self.request.headers.get("traceparent"),
            self.request.headers.get("tracestate"),
            self.request.headers.get("baggage"),
        )
        queryset = Booking.objects.all()
        
        # Filter by user role
        if getattr(self.request.user, 'role', None) != 'ADMIN':
            queryset = queryset.filter(user_id=self.request.user.id)
            
        # Filter by flight_id if provided (useful for Admin view by flight)
        flight_id = self.request.query_params.get('flight_id')
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)
            
        return queryset

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        flight_id = serializer.validated_data['flight_id']
        seats_needed = serializer.validated_data['passengers']
        
        flight_url = f"{settings.FLIGHT_ADMIN_SERVICE_URL}/{flight_id}/reserve_seat/"

        headers = {'X-Service-API-Key': settings.SERVICE_API_KEY}
        inject(headers)
        for _ in range(seats_needed):
            response = requests.post(flight_url, headers=headers)
            if response.status_code != 200:
                return Response(
                    {
                        "error": "Failed to reserve seat",
                        "upstream_status": response.status_code,
                        "upstream_response": response.text,
                    },
                    status=response.status_code
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

            # Check if flight has departed
            flight_url = f"{settings.FLIGHT_SERVICE_URL}/{booking.flight_id}/"
            headers = {'X-Service-API-Key': settings.SERVICE_API_KEY}
            inject(headers)
            flight_response = requests.get(flight_url, headers=headers)
            if flight_response.status_code != 200:
                return Response({"error": "Unable to verify flight details"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            flight_data = flight_response.json()
            departure_time_str = flight_data.get('departure_time')
            if not departure_time_str:
                return Response({"error": "Flight departure time not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Parse departure time (assuming ISO format)
            departure_time = datetime.datetime.fromisoformat(departure_time_str.replace('Z', '+00:00'))
            if departure_time <= datetime.datetime.now(datetime.timezone.utc):
                return Response({"error": "Cannot cancel booking after flight departure"}, status=status.HTTP_400_BAD_REQUEST)

            seats_to_release = booking.passengers.count() or 1
            
            flight_url = f"{settings.FLIGHT_ADMIN_SERVICE_URL}/{booking.flight_id}/release_seat/"
            
            headers = {'X-Service-API-Key': settings.SERVICE_API_KEY}
            inject(headers)
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


from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    logger.info(
        "Incoming trace headers: traceparent=%s tracestate=%s baggage=%s",
        request.headers.get("traceparent"),
        request.headers.get("tracestate"),
        request.headers.get("baggage"),
    )
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)