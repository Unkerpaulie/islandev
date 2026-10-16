from django import forms

from .models import Subscriber


class WorkshopIntakeForm(forms.Form):
    """
    Workshop booking / prospect intake form.

    Collects enough business context to qualify the prospect and identify the
    right stakeholder contact. Data is forwarded to the agents system via the
    internal intake API — nothing is stored locally.
    """
    company_name = forms.CharField(
        max_length=255,
        label='Business / Company Name',
        error_messages={'required': 'Please enter your business name.'},
    )
    industry = forms.CharField(
        max_length=128,
        label='Industry / Type of Business',
        required=False,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="What's your biggest operational challenge?",
        required=False,
        help_text='Optional — helps me come prepared.',
    )
    name = forms.CharField(
        max_length=150,
        label='Your Name',
        error_messages={'required': 'Please enter your name.'},
    )
    role = forms.CharField(
        max_length=100,
        label='Your Title / Role',
        required=False,
    )
    email = forms.EmailField(
        label='Email Address',
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.',
        },
    )


class ContactMessageForm(forms.Form):
    """
    General contact / send-a-message form.

    Data is forwarded to the agents system's inquiry endpoint — nothing stored
    locally in islandev.
    """
    name = forms.CharField(
        max_length=150,
        label='Your Name',
        error_messages={'required': 'Please enter your name.'},
    )
    email = forms.EmailField(
        label='Email Address',
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.',
        },
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label='Your Message',
        error_messages={'required': 'Please write a message.'},
    )


class SubscriberForm(forms.ModelForm):
    """Newsletter signup form used by the homepage newsletter section."""

    class Meta:
        model = Subscriber
        fields = ['name', 'email']

    def validate_unique(self):
        """Suppress uniqueness error on email — re-subscribe is idempotent."""
        return

    def save(self, commit=True):
        email = self.cleaned_data['email']
        name = self.cleaned_data['name']
        obj, _ = Subscriber.objects.update_or_create(
            email=email,
            defaults={'name': name, 'is_active': True},
        )
        return obj
