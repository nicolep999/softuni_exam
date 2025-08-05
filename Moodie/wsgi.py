"""
WSGI config for Moodie project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings if on Railway
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Moodie.settings_production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Moodie.settings")

application = get_wsgi_application()
