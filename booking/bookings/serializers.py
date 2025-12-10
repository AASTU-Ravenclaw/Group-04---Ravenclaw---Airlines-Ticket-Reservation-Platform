from rest_framework import serializers
from .models import Booking, Passenger

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'email', 'passport_number']

class BookingSerializer(serializers.ModelSerializer):
    passengers = serializers.IntegerField(write_only=True, min_value=1, max_value=10)
    passengers_details = PassengerSerializer(source='passengers', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'flight_id', 'status', 'booking_date', 'passengers', 'passengers_details']
        read_only_fields = ['booking_id', 'status', 'booking_date', 'passengers_details']

    def create(self, validated_data):
        passengers_count = validated_data.pop('passengers')
        # user_id is passed manually in perform_create within the view
        booking = Booking.objects.create(**validated_data)
        
        # Create dummy passengers for demo purposes
        for i in range(passengers_count):
            Passenger.objects.create(
                booking=booking,
                first_name=f"Passenger{i+1}",
                last_name="Doe",
                email=f"passenger{i+1}@example.com"
            )
            
        return booking