from django.test import TestCase, override_settings
from django.urls import reverse


# Prod settings have SECURE_SSL_REDIRECT=True (causes 301 in tests) and use
# CompressedManifestStaticFilesStorage (requires a current staticfiles manifest
# to resolve {% static %} tags). Both are overridden here so template-rendering
# tests produce correct results without depending on deployment environment state.
BASE_OVERRIDES = dict(
    SECURE_SSL_REDIRECT=False,
    SECURE_HSTS_SECONDS=0,
    STORAGES={
        'default':     {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)


@override_settings(**BASE_OVERRIDES)
class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_services_returns_200(self):
        response = self.client.get(reverse('core:services'))
        self.assertEqual(response.status_code, 200)
