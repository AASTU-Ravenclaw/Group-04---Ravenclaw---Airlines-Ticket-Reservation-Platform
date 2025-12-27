from rest_framework import serializers
from .models import Location, Flight

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class FlightReadSerializer(serializers.ModelSerializer):
    """ Serializer for Reading (GET) - includes nested location data """
    departure_location = LocationSerializer(read_only=True)
    arrival_location = LocationSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'

class FlightWriteSerializer(serializers.ModelSerializer):
    """ Serializer for Writing (POST/PUT) - accepts airport codes for locations """
    departure_location = serializers.CharField(write_only=True)
    arrival_location = serializers.CharField(write_only=True)
    
    class Meta:
        model = Flight
        fields = ['flight_number', 'departure_location', 'arrival_location', 
                 'departure_time', 'arrival_time', 'total_seats', 'available_seats', 'price']

    def validate_departure_location(self, value):
        try:
            return Location.objects.get(airport_code__iexact=value)
        except Location.DoesNotExist:
            raise serializers.ValidationError(f"Location with airport code '{value}' does not exist.")

    def validate_arrival_location(self, value):
        try:
            return Location.objects.get(airport_code__iexact=value)
        except Location.DoesNotExist:
            raise serializers.ValidationError(f"Location with airport code '{value}' does not exist.")

    def validate(self, data):
        if data['departure_location'] == data['arrival_location']:
            raise serializers.ValidationError("Departure and Arrival locations cannot be the same.")
        if data['available_seats'] > data['total_seats']:
            raise serializers.ValidationError("Available seats cannot exceed total seats.")
        return data