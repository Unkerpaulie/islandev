from django.db import models
from django.utils import timezone


class BookingRequest(models.Model):
    """A request to book a free consultation, submitted from the /book page."""

    class ServiceInterest(models.TextChoices):
        DIGITAL_CONSULTATION = 'digital_consultation', 'Digital Consultation'
        CUSTOM_WEB_APP = 'custom_web_app', 'Custom Web Application'
        BUSINESS_INTELLIGENCE = 'business_intelligence', 'Business Intelligence'
        SOP_DEVELOPMENT = 'sop_development', 'SOP Development'
        INVOICE_SYSTEM = 'invoice_system', 'Invoice System'
        GENERAL_INQUIRY = 'general_inquiry', 'General Inquiry'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    name = models.CharField(max_length=150)
    business_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    service_interest = models.CharField(
        max_length=40, choices=ServiceInterest.choices, blank=True,
    )
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.preferred_date} {self.preferred_time} ({self.status})'


class ContactInquiry(models.Model):
    """A contact-page submission. Two distinct intents: clients and collaborators."""

    class InquiryType(models.TextChoices):
        CLIENT = 'client', 'Client'
        COLLABORATOR = 'collaborator', 'Collaborator'

    name = models.CharField(max_length=150)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=InquiryType.choices)
    message = models.TextField()

    submitted_at = models.DateTimeField(default=timezone.now)
    is_handled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = 'Contact inquiries'

    def __str__(self):
        return f'{self.name} ({self.get_inquiry_type_display()})'


class Subscriber(models.Model):
    """A newsletter subscriber from the homepage newsletter block."""

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.name} <{self.email}>'
