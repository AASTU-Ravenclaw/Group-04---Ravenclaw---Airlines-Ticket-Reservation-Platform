import os
from pathlib import Path
import logging

# Import OpenTelemetry configuration
try:
    import config.otel  # noqa
except ImportError:
    pass  # OpenTelemetry not available

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = False

ALLOWED_HOSTS = ['*']

# Security settings for Kubernetes
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

APPEND_SLASH = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'django_prometheus',
    'whitenoise',
    
    'bookings',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'bookings.authentication.HeaderAuthentication',
    ],
}

# DRF YASG Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'X-User-Id': {
            'type': 'apiKey',
            'name': 'X-User-Id',
            'in': 'header',
            'description': 'User ID header set by authentication middleware'
        },
        'X-User-Email': {
            'type': 'apiKey',
            'name': 'X-User-Email',
            'in': 'header',
            'description': 'User email header set by authentication middleware'
        },
        'X-User-Role': {
            'type': 'apiKey',
            'name': 'X-User-Role',
            'in': 'header',
            'description': 'User role header set by authentication middleware'
        }
    },
    'SECURITY_REQUIREMENTS': [
        {'X-User-Id': []},
        {'X-User-Email': []},
        {'X-User-Role': []}
    ],
    'DOC_EXPANSION': 'none',
}

# Service URLs (Internal Docker Network)
FLIGHT_SERVICE_URL = os.environ.get('FLIGHT_SERVICE_URL', 'http://flight-service:8000/api/v1/flights')

# Service-to-Service API Key (must match flight service)
SERVICE_API_KEY = os.environ.get('SERVICE_API_KEY', 'dev-service-key-12345')

# RabbitMQ Settings
RABBITMQ_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@rabbitmq.airlines.svc.cluster.local:5672/'

# CORS settings for frontend access
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        },
        'structured': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/booking_service.log',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'opentelemetry': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# OpenTelemetry Configuration
OPENTELEMETRY = {
    'SERVICE_NAME': 'booking-service',
    'SERVICE_VERSION': '1.0.0',
    'OTLP_ENDPOINT': os.environ.get('OTLP_ENDPOINT', 'http://otel-collector.observability.svc.cluster.local:4318'),
    'TRACES_EXPORTER': 'otlp',
    'METRICS_EXPORTER': 'otlp',
    'LOGS_EXPORTER': 'otlp',
}

# Create logs directory
os.makedirs('/app/logs', exist_ok=True)