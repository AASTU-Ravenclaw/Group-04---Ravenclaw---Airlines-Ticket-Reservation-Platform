import os
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):

        if os.environ.get("RUN_MAIN") == "true":
            from .consumer import run_consumer_thread

            run_consumer_thread()
