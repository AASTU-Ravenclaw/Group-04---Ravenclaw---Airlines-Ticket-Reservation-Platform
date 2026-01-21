from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers 
from django.db.models import F, Q
import datetime

from .models import Location, Flight
from .serializers import LocationSerializer, FlightReadSerializer, FlightCreateSerializer, FlightUpdateSerializer
from .permissions import IsAdminOrReadOnly, IsServiceAuthenticated

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    def destroy(self, request, *args, **kwargs):
        """Prevent deletion if location is used by any flights"""
        location = self.get_object()
        
        # Check if any flights use this location as departure or arrival
        flights_using_location = Flight.objects.filter(
            Q(departure_location=location) | Q(arrival_location=location)
        ).exists()
        
        if flights_using_location:
            return Response(
                {"error": "Cannot delete location that is used by existing flights"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('departure_time')
    permission_classes = [IsAdminOrReadOnly] 
    
    pagination_class = None 
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightReadSerializer
        elif self.action == 'create':
            return FlightCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FlightUpdateSerializer
        return FlightReadSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()
        new_status = instance.status
        # The serializer already publishes `flight_delayed` when it sets delayed due to a departure_time change.
        if old_status != new_status and new_status != 'delayed':
            self._publish_flight_status_change(instance, new_status)
        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        response = super().partial_update(request, *args, **kwargs)
        instance.refresh_from_db()
        new_status = instance.status
        if old_status != new_status and new_status != 'delayed':
            self._publish_flight_status_change(instance, new_status)
        return response

    def _publish_flight_status_change(self, flight, new_status):
        from .producer import publish_event
        event_type = f"flight_{new_status.lower()}"
        event_data = {
            "flight_id": str(flight.flight_id),
            "flight_number": flight.flight_number,
            "departure_location": flight.departure_location.airport_code,
            "arrival_location": flight.arrival_location.airport_code,
            "departure_time": flight.departure_time.isoformat(),
            "arrival_time": flight.arrival_time.isoformat(),
            "status": new_status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        if new_status == "delayed":
            # Assume some delay logic, for now just publish
            event_data["new_departure_time"] = flight.departure_time.isoformat()
        print(f"Publishing flight event: {event_type} for flight {flight.flight_number}")
        publish_event(event_type, event_data)

    def destroy(self, request, *args, **kwargs):
        """Only allow deletion if no seats are booked (total_seats == available_seats)"""
        flight = self.get_object()
        if flight.total_seats != flight.available_seats:
            return Response(
                {"error": "Cannot delete flight with booked seats"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):

        queryset = Flight.objects.all().order_by('departure_time')
        
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        date = request.query_params.get('date')

        if origin:
            queryset = queryset.filter(departure_location__airport_code__iexact=origin) | \
                       queryset.filter(departure_location__city__icontains=origin)
        
        if destination:
            queryset = queryset.filter(arrival_location__airport_code__iexact=destination) | \
                       queryset.filter(arrival_location__city__icontains=destination)
            
        if date:
            queryset = queryset.filter(departure_time__date=date)

        serializer = FlightReadSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsServiceAuthenticated]) 
    def reserve_seat(self, request, pk=None):

        try:
            flight = self.get_object()
            
            if flight.available_seats < 1:
                return Response(
                    {"error": "Flight is full"}, 
                    status=status.HTTP_409_CONFLICT
                )

            flight.available_seats = F('available_seats') - 1
            flight.save()
            flight.refresh_from_db()
            
            return Response(
                {"message": "Seat reserved", "remaining_seats": flight.available_seats}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsServiceAuthenticated])
    def release_seat(self, request, pk=None):

        try:
            flight = self.get_object()
            
            flight.available_seats = F('available_seats') + 1
            flight.save()
            flight.refresh_from_db()
            
            return Response(
                {"message": "Seat released", "remaining_seats": flight.available_seats}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)