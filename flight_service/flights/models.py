import uuid
from django.db import models

class Location(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    airport_code = models.CharField(max_length=10, unique=True) # e.g., ADD, JFK
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.airport_code} - {self.name}"

class Flight(models.Model):
    flight_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flight_number = models.CharField(max_length=50) # e.g., ET-302
    
    # Relationships
    departure_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='departures'
    )
    arrival_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='arrivals'
    )
    
    # Times
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    # Capacity
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flight_number} ({self.departure_location.airport_code} -> {self.arrival_location.airport_code})"