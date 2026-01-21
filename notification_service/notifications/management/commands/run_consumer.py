from django.core.management.base import BaseCommand
from notifications.consumer import start_consumer

class Command(BaseCommand):
    help = 'Runs the notification service consumer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Notification Consumer...'))
        start_consumer()
