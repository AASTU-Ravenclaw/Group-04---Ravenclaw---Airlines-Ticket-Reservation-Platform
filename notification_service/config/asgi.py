import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

# Import after setup
from django.urls import path
from notifications.consumers import NotificationConsumer
from notifications.consumer import run_consumer_thread

# Start the consumer thread
# run_consumer_thread()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/notifications/<str:user_id>/<str:token>/", NotificationConsumer.as_asgi()),
    ]),
})
