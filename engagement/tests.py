from datetime import date, time

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
    def test_get_renders_page(self):
        response = self.client.get(reverse('engagement:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'I Need Digital Solutions')
        self.assertContains(response, 'I Want to Collaborate')

    def test_valid_post_creates_inquiry_and_redirects(self):
        response = self.client.post(reverse('engagement:contact'), {
            'inquiry_type': 'client',
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'company': 'Acme',
            'message': 'I need a custom dashboard.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=client', response['Location'])
        inquiry = ContactInquiry.objects.get(email='jane@example.com')
        self.assertEqual(inquiry.inquiry_type, ContactInquiry.InquiryType.CLIENT)

    def test_invalid_inquiry_type_rejected(self):
        response = self.client.post(reverse('engagement:contact'), {
            'inquiry_type': 'hacker',
            'name': 'X', 'email': 'x@example.com', 'message': 'hi',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactInquiry.objects.exists())

    def test_missing_required_fields_rejected(self):
        response = self.client.post(reverse('engagement:contact'), {
            'inquiry_type': 'collaborator',
            'name': '', 'email': 'not-an-email', 'message': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactInquiry.objects.exists())


class BookViewTests(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(reverse('engagement:book'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book a Discovery Call')

    def test_valid_post_creates_booking_and_redirects(self):
        response = self.client.post(reverse('engagement:book'), {
            'name': 'Pat Lee',
            'email': 'pat@example.com',
            'business_name': 'Pat Co',
            'service_interest': BookingRequest.ServiceInterest.CUSTOM_WEB_APP,
            'preferred_date': '2030-06-15',
            'preferred_time': '10:00',
            'message': 'Looking to digitize ops.',
        })
        self.assertEqual(response.status_code, 302)
        booking = BookingRequest.objects.get(email='pat@example.com')
        self.assertIn(f'booked={booking.pk}', response['Location'])
        self.assertEqual(booking.status, BookingRequest.Status.PENDING)

    def test_missing_required_fields_rejected(self):
        response = self.client.post(reverse('engagement:book'), {
            'name': '', 'email': 'bad', 'preferred_date': '', 'preferred_time': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(BookingRequest.objects.exists())

    def test_booked_param_shows_confirmation(self):
        booking = BookingRequest.objects.create(
            name='Pat Lee',
            email='pat@example.com',
            preferred_date=date(2030, 6, 15),
            preferred_time=time(10, 0),
        )
        response = self.client.get(reverse('engagement:book') + f'?booked={booking.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Consultation Request Received')
        self.assertContains(response, 'Pat Lee')
