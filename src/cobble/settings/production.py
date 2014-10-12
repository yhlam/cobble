import os

import dj_database_url

from .base import *


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

TEMPLATE_DEBUG = False

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    # Parse database configuration from $DATABASE_URL
    'default': dj_database_url.config(),
}
