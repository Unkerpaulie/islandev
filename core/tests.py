from django.test import TestCase, override_settings
from django.urls import reverse


# Prod settings have SECURE_SSL_REDIRECT=True; the test client follows the
# redirect and never reaches the view. Suppressing it here is the standard
# fix — it doesn't change what is tested in production.
@override_settings(SECURE_SSL_REDIRECT=False, SECURE_HSTS_SECONDS=0)
class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_services_returns_200(self):
        response = self.client.get(reverse('core:services'))
        self.assertEqual(response.status_code, 200)
