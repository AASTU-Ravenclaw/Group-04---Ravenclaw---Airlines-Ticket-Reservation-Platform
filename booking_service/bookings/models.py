import uuid
from django.db import models

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    flight_id = models.UUIDField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.status}"

class Passenger(models.Model):
    passenger_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    passport_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"