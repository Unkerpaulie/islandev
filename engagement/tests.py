from datetime import date, time

from django.test import TestCase

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
