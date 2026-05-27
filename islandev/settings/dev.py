"""
Development settings.

Loaded when DJANGO_SETTINGS_MODULE=islandev.settings.dev (the default in
manage.py and in the local .env). Optimised for local iteration: SQLite,
DEBUG on by default, no security flags engaged.
"""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# In dev, allow WhiteNoise to serve straight from STATICFILES_DIRS without
# requiring a collectstatic step.
WHITENOISE_USE_FINDERS = True
