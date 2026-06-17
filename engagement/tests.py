from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import BookingRequest, ContactInquiry, Subscriber


class BookingRequestModelTests(TestCase):
    def test_default_status_is_pending(self):
        booking = BookingRequest.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            preferred_date=date(2026, 6, 1),
            preferred_time=time(10, 30),
        )
        self.assertEqual(booking.status, BookingRequest.Status.PENDING)


class ContactInquiryModelTests(TestCase):
    def test_str_includes_inquiry_type(self):
        inquiry = ContactInquiry.objects.create(
            name='Sam Lee',
            email='sam@example.com',
            inquiry_type=ContactInquiry.InquiryType.COLLABORATOR,
            message='Interested in collaborating.',
        )
        self.assertIn('Collaborator', str(inquiry))


class SubscriberModelTests(TestCase):
    def test_email_must_be_unique(self):
        Subscriber.objects.create(name='A', email='a@example.com')
        with self.assertRaises(Exception):
            Subscriber.objects.create(name='B', email='a@example.com')


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
        response = self.client.post(reverse('engagement:subscribe'), {'name': '', 'email': 'nope'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Subscriber.objects.exists())

    def test_duplicate_email_is_idempotent(self):
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


class ContactViewTests(TestCase):
    """Tests for the unified contact/booking page (mode=contact path)."""

    def test_get_default_renders_contact_mode(self):
        response = self.client.get(reverse('engagement:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Let\'s Start a Conversation')
        # initial_mode context should default to contact when no ?mode param
        self.assertEqual(response.context['initial_mode'], 'contact')

    def test_get_with_mode_book_sets_initial_mode(self):
        response = self.client.get(reverse('engagement:contact') + '?mode=book')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['initial_mode'], 'book')

    @patch('engagement.views.send_contact_email')
    def test_valid_contact_post_creates_inquiry_and_redirects(self, mock_email):
        response = self.client.post(reverse('engagement:contact'), {
            'mode': 'contact',
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'company': 'Acme',
            'message': 'I need a custom dashboard.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=contact', response['Location'])
        inquiry = ContactInquiry.objects.get(email='jane@example.com')
        self.assertEqual(inquiry.inquiry_type, ContactInquiry.InquiryType.CLIENT)
        mock_email.assert_called_once_with(inquiry)

    @patch('engagement.views.send_contact_email')
    def test_contact_missing_required_fields_returns_400(self, mock_email):
        response = self.client.post(reverse('engagement:contact'), {
            'mode': 'contact',
            'name': '', 'email': 'not-an-email', 'message': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactInquiry.objects.exists())
        mock_email.assert_not_called()

    def test_get_success_contact_shows_confirmation(self):
        response = self.client.get(reverse('engagement:contact') + '?success=contact')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Message Received')

    def test_get_success_booking_shows_confirmation(self):
        response = self.client.get(reverse('engagement:contact') + '?success=booking')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking Request Received')


class BookViewTests(TestCase):
    """Tests for the unified contact/booking page (mode=booking path) and the
    legacy /book/ redirect."""

    def test_legacy_book_url_redirects_to_contact(self):
        response = self.client.get(reverse('engagement:book'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/contact/', response['Location'])
        self.assertIn('mode=book', response['Location'])

    @patch('engagement.views.send_booking_email')
    def test_valid_booking_post_creates_booking_and_redirects(self, mock_email):
        response = self.client.post(reverse('engagement:contact'), {
            'mode': 'booking',
            'name': 'Pat Lee',
            'email': 'pat@example.com',
            'business_name': 'Pat Co',
            'service_interest': BookingRequest.ServiceInterest.CUSTOM_WEB_APP,
            'preferred_date': '2030-06-15',
            'preferred_time': '10:00',
            'message': 'Looking to digitize ops.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=booking', response['Location'])
        booking = BookingRequest.objects.get(email='pat@example.com')
        self.assertEqual(booking.status, BookingRequest.Status.PENDING)
        mock_email.assert_called_once_with(booking)

    @patch('engagement.views.send_booking_email')
    def test_booking_missing_date_time_returns_400(self, mock_email):
        response = self.client.post(reverse('engagement:contact'), {
            'mode': 'booking',
            'name': 'Pat Lee',
            'email': 'pat@example.com',
            'preferred_date': '',
            'preferred_time': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(BookingRequest.objects.exists())
        mock_email.assert_not_called()
