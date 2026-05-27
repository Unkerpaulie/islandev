"""
WSGI config for islandev project.

The DJANGO_SETTINGS_MODULE here is only a local-dev fallback. In production,
Gunicorn loads it from EnvironmentFile=<islandev_root>/.env via systemd.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'islandev.settings.dev')

application = get_wsgi_application()
