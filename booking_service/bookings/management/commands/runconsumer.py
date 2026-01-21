from django.core.management.base import BaseCommand
from bookings.consumer import start_flight_event_consumer


class Command(BaseCommand):
    help = 'Run the flight event consumer'

    def handle(self, *args, **options):
        self.stdout.write('Starting flight event consumer...')
        start_flight_event_consumer()