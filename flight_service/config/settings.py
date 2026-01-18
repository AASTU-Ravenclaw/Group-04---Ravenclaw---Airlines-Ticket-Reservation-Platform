import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = True

ALLOWED_HOSTS = ['*']

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
    'flights',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'flights.authentication.HeaderAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 1000,
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
# Service-to-Service API Key
SERVICE_API_KEY = os.environ.get('SERVICE_API_KEY', 'dev-service-key-12345')

# RabbitMQ Settings
RABBITMQ_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
RABBITMQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@rabbitmq.airlines.svc.cluster.local:5672/'
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
    'cache-control',
    'content-type',
    'dnt',
    'origin',
    'pragma',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
