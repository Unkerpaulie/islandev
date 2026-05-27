from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_services_returns_200(self):
        response = self.client.get(reverse('core:services'))
        self.assertEqual(response.status_code, 200)
