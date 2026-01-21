"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from config.otel import setup_opentelemetry
    setup_opentelemetry()
except Exception as e:
    print(f"Failed to setup OTEL in WSGI: {e}")

application = get_wsgi_application()
# application = WhiteNoise(application, root='/app/staticfiles')
