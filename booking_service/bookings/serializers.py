from rest_framework import serializers
from .models import Booking, Passenger

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'email', 'passport_number']
        extra_kwargs = {
            'email': {'required': False},
            'passport_number': {'required': False}
        }

class BookingSerializer(serializers.ModelSerializer):
    passengers = serializers.IntegerField(write_only=True, min_value=1, max_value=10, required=False)
    passengers_list = PassengerSerializer(many=True, write_only=True, required=False)
    passengers_details = PassengerSerializer(source='passengers', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'flight_id', 'status', 'booking_date', 'passengers', 'passengers_list', 'passengers_details']
        read_only_fields = ['booking_id', 'status', 'booking_date', 'passengers_details']

    def create(self, validated_data):
        # Extract passengers data
        passengers_data = validated_data.pop('passengers_list', [])
        passengers_count = validated_data.pop('passengers', len(passengers_data) if passengers_data else 1)
        
        # user_id is passed manually in perform_create within the view
        # Correctly create booking without passing 'passengers' reverse relation
        booking = Booking.objects.create(**validated_data)
        
        if passengers_data:
            for passenger_data in passengers_data:
                Passenger.objects.create(booking=booking, **passenger_data)
        else:
            # Fallback to dummy passengers if no list provided (backward compatibility)
            for i in range(passengers_count):
                Passenger.objects.create(
                    booking=booking,
                    first_name=f"Passenger{i+1}",
                    last_name="Doe",
                    email=f"passenger{i+1}@example.com"
                )
            
        return booking
