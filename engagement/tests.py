"""
engagement/tests.py

Tests for the engagement app's current form layer:
- WorkshopIntakeForm  (prospect intake → agents endpoint)
- ContactMessageForm  (general message → agents endpoint)
- SubscriberForm      (newsletter signup → local DB)
- contact view        (drives both intake forms)
- subscribe view

BookingRequest and ContactInquiry have been removed from this project.
Those models and their tests no longer exist here; the intake logic lives
in the agents system (agents.islan.dev) and is exercised via mock.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Subscriber


# ---------------------------------------------------------------------------
# Base settings override — all tests run with prod settings (the active
# DJANGO_SETTINGS_MODULE during deployment). SECURE_SSL_REDIRECT causes
# 301 redirects in the test client; suppressing it here is standard practice
# and doesn't change what is tested in production.
# ---------------------------------------------------------------------------

BASE_OVERRIDES = dict(
    SECURE_SSL_REDIRECT=False,
    SECURE_HSTS_SECONDS=0,
    # Prod settings use CompressedManifestStaticFilesStorage, which requires a
    # current staticfiles manifest to resolve {% static %} tags in templates.
    # Plain StaticFilesStorage returns direct URLs without needing the manifest,
    # making all template-rendering tests reliable regardless of whether
    # collectstatic has run yet in this deployment cycle.
    STORAGES={
        'default':     {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)


# ---------------------------------------------------------------------------
# Subscriber model
# ---------------------------------------------------------------------------

@override_settings(**BASE_OVERRIDES)
class SubscriberModelTests(TestCase):
    def test_email_must_be_unique(self):
        Subscriber.objects.create(name='A', email='a@example.com')
        with self.assertRaises(Exception):
            Subscriber.objects.create(name='B', email='a@example.com')


# ---------------------------------------------------------------------------
# Subscribe view (/subscribe/)
# ---------------------------------------------------------------------------

@override_settings(**BASE_OVERRIDES)
class SubscribeViewTests(TestCase):

    def test_get_is_not_allowed(self):
        response = self.client.get(reverse('engagement:subscribe'))
        self.assertEqual(response.status_code, 405)

    def test_valid_post_creates_subscriber_and_redirects(self):
        response = self.client.post(
            reverse('engagement:subscribe'),
            {'name': 'Pat', 'email': 'pat@example.com'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('subscribed=1', response['Location'])
        self.assertTrue(Subscriber.objects.filter(email='pat@example.com').exists())

    def test_invalid_post_rerenders_with_400(self):
        response = self.client.post(
            reverse('engagement:subscribe'),
            {'name': '', 'email': 'nope'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Subscriber.objects.exists())

    def test_duplicate_email_updates_name_and_reactivates(self):
        Subscriber.objects.create(name='Old Name', email='dup@example.com', is_active=False)
        response = self.client.post(
            reverse('engagement:subscribe'),
            {'name': 'New Name', 'email': 'dup@example.com'},
        )
        self.assertEqual(response.status_code, 302)
        sub = Subscriber.objects.get(email='dup@example.com')
        self.assertEqual(sub.name, 'New Name')
        self.assertTrue(sub.is_active)
        self.assertEqual(Subscriber.objects.filter(email='dup@example.com').count(), 1)


# ---------------------------------------------------------------------------
# Contact view GET — /contact/
# ---------------------------------------------------------------------------

@override_settings(**BASE_OVERRIDES)
class ContactViewGetTests(TestCase):

    def test_get_default_opens_contact_mode(self):
        response = self.client.get(reverse('engagement:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['initial_mode'], 'contact')

    def test_get_mode_workshop_sets_initial_mode(self):
        response = self.client.get(reverse('engagement:contact') + '?mode=workshop')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['initial_mode'], 'workshop')

    def test_success_workshop_shows_confirmation(self):
        response = self.client.get(reverse('engagement:contact') + '?success=workshop')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workshop Request Received')

    def test_success_contact_shows_confirmation(self):
        response = self.client.get(reverse('engagement:contact') + '?success=contact')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Message Received')

    def test_invalid_success_param_renders_form(self):
        response = self.client.get(reverse('engagement:contact') + '?success=junk')
        self.assertEqual(response.status_code, 200)
        # Should show the form, not a success state
        self.assertFalse(response.context.get('success'))


# ---------------------------------------------------------------------------
# Contact view POST — workshop intake
# The view calls submit_prospect() from engagement.intake, which is mocked
# so no real network call is made.
# ---------------------------------------------------------------------------

@override_settings(**BASE_OVERRIDES)
class WorkshopIntakePostTests(TestCase):

    VALID = {
        'mode':         'workshop',
        'company_name': 'Acme Construction Ltd',
        'industry':     'Construction',
        'description':  'We need better job tracking.',
        'name':         'Jane Smith',
        'role':         'Director',
        'email':        'jane@acme.com',
    }

    @patch('engagement.views.submit_prospect')
    def test_valid_post_calls_agents_and_redirects(self, mock_submit):
        mock_submit.return_value = (True, {'id': 42})
        response = self.client.post(reverse('engagement:contact'), self.VALID)
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=workshop', response['Location'])
        mock_submit.assert_called_once_with(
            company_name='Acme Construction Ltd',
            industry='Construction',
            description='We need better job tracking.',
            name='Jane Smith',
            role='Director',
            email='jane@acme.com',
        )

    @patch('engagement.views.submit_prospect')
    def test_optional_fields_may_be_omitted(self, mock_submit):
        mock_submit.return_value = (True, {'id': 43})
        data = {'mode': 'workshop', 'company_name': 'Solo Co', 'name': 'Mark', 'email': 'm@solo.com'}
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 302)
        # industry, description, role all default to empty string
        mock_submit.assert_called_once_with(
            company_name='Solo Co',
            industry='',
            description='',
            name='Mark',
            role='',
            email='m@solo.com',
        )

    @patch('engagement.views.submit_prospect')
    def test_agents_failure_returns_500_with_form(self, mock_submit):
        mock_submit.return_value = (False, {'error': 'Connection refused'})
        response = self.client.post(reverse('engagement:contact'), self.VALID)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.context['submission_error'])
        # The form is re-rendered with the user's input so they don't have to retype.
        self.assertContains(response, 'Acme Construction Ltd', status_code=500)

    @patch('engagement.views.submit_prospect')
    def test_missing_company_name_returns_400_without_calling_agents(self, mock_submit):
        data = dict(self.VALID)
        data['company_name'] = ''
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 400)
        mock_submit.assert_not_called()

    @patch('engagement.views.submit_prospect')
    def test_missing_name_returns_400_without_calling_agents(self, mock_submit):
        data = dict(self.VALID)
        data['name'] = ''
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 400)
        mock_submit.assert_not_called()

    @patch('engagement.views.submit_prospect')
    def test_invalid_email_returns_400_without_calling_agents(self, mock_submit):
        data = dict(self.VALID)
        data['email'] = 'not-an-email'
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 400)
        mock_submit.assert_not_called()


# ---------------------------------------------------------------------------
# Contact view POST — general message
# ---------------------------------------------------------------------------

@override_settings(**BASE_OVERRIDES)
class ContactMessagePostTests(TestCase):

    VALID = {
        'mode':    'contact',
        'name':    'Sam Lee',
        'email':   'sam@example.com',
        'message': 'I have a question about your services.',
    }

    @patch('engagement.views.submit_inquiry')
    def test_valid_post_calls_agents_and_redirects(self, mock_submit):
        mock_submit.return_value = (True, {'id': 7})
        response = self.client.post(reverse('engagement:contact'), self.VALID)
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=contact', response['Location'])
        mock_submit.assert_called_once_with(
            name='Sam Lee',
            email='sam@example.com',
            message='I have a question about your services.',
        )

    @patch('engagement.views.submit_inquiry')
    def test_agents_failure_returns_500_with_form(self, mock_submit):
        mock_submit.return_value = (False, {'error': 'Timeout'})
        response = self.client.post(reverse('engagement:contact'), self.VALID)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.context['submission_error'])

    @patch('engagement.views.submit_inquiry')
    def test_missing_message_returns_400_without_calling_agents(self, mock_submit):
        data = dict(self.VALID)
        data['message'] = ''
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 400)
        mock_submit.assert_not_called()

    @patch('engagement.views.submit_inquiry')
    def test_missing_email_returns_400_without_calling_agents(self, mock_submit):
        data = dict(self.VALID)
        data['email'] = ''
        response = self.client.post(reverse('engagement:contact'), data)
        self.assertEqual(response.status_code, 400)
        mock_submit.assert_not_called()
