from rest_framework import serializers
from .models import Location, Flight
from .producer import publish_event
import datetime
from django.utils import timezone

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

class FlightCreateSerializer(serializers.ModelSerializer):
    """ Serializer for Creating (POST) - accepts airport codes for locations """
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
        if data['arrival_time'] <= data['departure_time']:
            raise serializers.ValidationError("Arrival time must be after departure time.")
        return data

class FlightUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for Updating (PUT/PATCH) - restricted fields """
    
    class Meta:
        model = Flight
        fields = ['departure_time', 'arrival_time', 'status']

    def validate_departure_time(self, value):
        """Only allow delaying departure time (making it later)"""
        if self.instance:
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
            if value < self.instance.departure_time:
                raise serializers.ValidationError("Departure time can only be delayed, not moved earlier.")
        return value

    def validate_arrival_time(self, value):
        """Ensure arrival time is after departure time"""
        departure_time = self.initial_data.get('departure_time', getattr(self.instance, 'departure_time', None))
        if departure_time:
            if isinstance(departure_time, str):
                from django.utils.dateparse import parse_datetime
                departure_time = parse_datetime(departure_time)
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
            if timezone.is_naive(departure_time):
                departure_time = timezone.make_aware(departure_time)
            if value <= departure_time:
                raise serializers.ValidationError("Arrival time must be after departure time.")
        return value

    def validate_status(self, value):
        """Allow changing status to scheduled, boarding, departed, cancelled, or delayed"""
        allowed_statuses = ['scheduled', 'boarding', 'departed', 'cancelled', 'delayed']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status can only be changed to: {', '.join(allowed_statuses)}")
        return value

    def validate(self, data):
        """Additional validation for updates"""
        # Make datetime fields timezone-aware
        for field in ['departure_time', 'arrival_time']:
            if field in data and data[field] and timezone.is_naive(data[field]):
                data[field] = timezone.make_aware(data[field])
        
        if self.instance:
            # If status is departed, no further editing allowed
            if self.instance.status == 'departed':
                raise serializers.ValidationError("Cannot edit a flight that has departed.")
            
            # Check for departure time change (delay)
            departure_time_changed = 'departure_time' in data and data['departure_time'] != self.instance.departure_time
            
            # Check for status changes
            new_status = data.get('status', self.instance.status)
            status_changed = new_status != self.instance.status
            
            # If departure_time is being changed, set status to delayed
            if departure_time_changed:
                data['status'] = 'delayed'
                new_status = 'delayed'
            
            # Publish events based on changes
            if departure_time_changed:
                # Flight delayed event
                event_data = {
                    "flight_id": str(self.instance.flight_id),
                    "flight_number": self.instance.flight_number,
                    "old_departure_time": self.instance.departure_time.isoformat(),
                    "new_departure_time": data['departure_time'].isoformat(),
                    "status": "delayed",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                publish_event('flight_delayed', event_data)
            
            if status_changed and not departure_time_changed:  # Don't publish status change if it was auto-set due to delay
                if new_status == 'cancelled':
                    event_data = {
                        "flight_id": str(self.instance.flight_id),
                        "flight_number": self.instance.flight_number,
                        "departure_time": self.instance.departure_time.isoformat(),
                        "status": "cancelled",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    publish_event('flight_cancelled', event_data)
                elif new_status == 'boarding':
                    event_data = {
                        "flight_id": str(self.instance.flight_id),
                        "flight_number": self.instance.flight_number,
                        "departure_time": self.instance.departure_time.isoformat(),
                        "status": "boarding",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    publish_event('flight_boarding', event_data)
        
        return data