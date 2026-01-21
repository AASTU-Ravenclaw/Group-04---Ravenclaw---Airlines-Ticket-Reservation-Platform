from django.core.management.base import BaseCommand
from bookings.consumer import start_flight_event_consumer

class Command(BaseCommand):
    help = 'Runs the booking service flight event consumer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Flight Event Consumer...'))
        start_flight_event_consumer()
