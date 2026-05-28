from django import forms

from .models import BookingRequest, ContactInquiry, Subscriber


class SubscriberForm(forms.ModelForm):
    """Newsletter signup form used by the homepage newsletter section."""

    class Meta:
        model = Subscriber
        fields = ['name', 'email']

    def validate_unique(self):
        """Suppress the default uniqueness check on email.

        Submitting the same email twice should not be an error from the user's
        perspective — it should re-subscribe them. The idempotent upsert
        happens in save() via update_or_create.
        """
        return

    def save(self, commit=True):
        email = self.cleaned_data['email']
        name = self.cleaned_data['name']
        obj, _ = Subscriber.objects.update_or_create(
            email=email,
            defaults={'name': name, 'is_active': True},
        )
        return obj


class ContactInquiryForm(forms.ModelForm):
    """Contact page submission. inquiry_type is set by the view (client/collaborator)
    rather than the form so the user picks it via the portal they expand."""

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'company', 'message']


class BookingRequestForm(forms.ModelForm):
    """Consultation booking. The multi-step UI happens client-side in Alpine;
    on final submit all fields arrive together and we validate the lot here."""

    class Meta:
        model = BookingRequest
        fields = [
            'name', 'business_name', 'email', 'service_interest',
            'preferred_date', 'preferred_time', 'message',
        ]
