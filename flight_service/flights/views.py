from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers 
from django.db.models import F

from .models import Location, Flight
from .serializers import LocationSerializer, FlightReadSerializer, FlightWriteSerializer
from .permissions import IsAdminOrReadOnly, IsServiceAuthenticated

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdminOrReadOnly]

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().order_by('departure_time')
    permission_classes = [IsAdminOrReadOnly] 
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightReadSerializer
        return FlightWriteSerializer

    def list(self, request, *args, **kwargs):

        queryset = self.queryset
        
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