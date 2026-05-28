from datetime import date, timedelta

from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import BookingRequestForm, ContactInquiryForm, SubscriberForm
from .models import BookingRequest, ContactInquiry


INQUIRY_TYPES = {c.value for c in ContactInquiry.InquiryType}

# Presentation data for the two contact portals. Kept here (rather than in a
# separate content module) because the labels and inquiry_type values are
# tightly coupled to the view's POST handling.
CONTACT_PORTALS = [
    {
        'key': 'client',
        'label': 'I Need Digital Solutions',
        'sub': 'For businesses looking to transform their operations',
        'icon_svg': '<path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/><path d="M9 9v.01"/><path d="M9 12v.01"/><path d="M9 15v.01"/><path d="M9 18v.01"/>',
        'company_label': 'Business / Company Name',
        'company_placeholder': 'Acme Ltd.',
        'message_label': 'Tell me about your business challenge',
        'message_placeholder': 'Describe your current process and what you are trying to improve...',
    },
    {
        'key': 'collaborator',
        'label': 'I Want to Collaborate',
        'sub': 'For developers and digital service providers',
        'icon_svg': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        'company_label': 'Organization / GitHub / Website',
        'company_placeholder': 'github.com/yourhandle',
        'message_label': 'What are you interested in collaborating on?',
        'message_placeholder': 'Describe your skills, what you are working on, or how you want to connect...',
    },
]

# Each slot is (display label, ISO 24-hour value Django's TimeField accepts).
TIME_SLOTS = [
    ('9:00 AM', '09:00'), ('9:30 AM', '09:30'),
    ('10:00 AM', '10:00'), ('10:30 AM', '10:30'),
    ('11:00 AM', '11:00'), ('11:30 AM', '11:30'),
    ('2:00 PM', '14:00'), ('2:30 PM', '14:30'),
    ('3:00 PM', '15:00'), ('3:30 PM', '15:30'),
    ('4:00 PM', '16:00'), ('4:30 PM', '16:30'),
]


def _next_n_weekdays(n=14):
    """Return the next n weekdays (Mon-Fri) starting from tomorrow."""
    days = []
    d = date.today() + timedelta(days=1)
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def contact(request):
    """Two-portal contact page. POST creates a ContactInquiry; the inquiry_type
    is supplied as a hidden field by whichever portal form was submitted."""
    if request.method == 'POST':
        inquiry_type = request.POST.get('inquiry_type', '')
        form = ContactInquiryForm(request.POST)
        if inquiry_type in INQUIRY_TYPES and form.is_valid():
            obj = form.save(commit=False)
            obj.inquiry_type = inquiry_type
            obj.save()
            return redirect(
                reverse('engagement:contact') + f'?success={inquiry_type}#contact'
            )
        return render(request, 'engagement/contact.html', {
            'form': form,
            'portals': CONTACT_PORTALS,
            'initial_active': inquiry_type if inquiry_type in INQUIRY_TYPES else '',
            'success': '',
        }, status=400)

    success = request.GET.get('success', '')
    if success not in INQUIRY_TYPES:
        success = ''
    return render(request, 'engagement/contact.html', {
        'form': ContactInquiryForm(),
        'portals': CONTACT_PORTALS,
        'initial_active': success,
        'success': success,
    })


def book(request):
    """Three-step booking page. The wizard UI is Alpine-driven on the client;
    the server only sees the final submission with all fields filled in."""
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect(
                reverse('engagement:book') + f'?booked={booking.pk}'
            )
        return render(request, 'engagement/book.html', {
            'form': form,
            'dates': _next_n_weekdays(),
            'time_slots': TIME_SLOTS,
            'service_choices': BookingRequest.ServiceInterest.choices,
            'booked': None,
        }, status=400)

    booked_pk = request.GET.get('booked')
    booked = None
    if booked_pk and booked_pk.isdigit():
        booked = BookingRequest.objects.filter(pk=int(booked_pk)).first()
    return render(request, 'engagement/book.html', {
        'form': BookingRequestForm(),
        'dates': _next_n_weekdays(),
        'time_slots': TIME_SLOTS,
        'service_choices': BookingRequest.ServiceInterest.choices,
        'booked': booked,
    })


def subscribe(request):
    """Handle the homepage newsletter signup.

    Accepts POST only. On success, redirects back to the home page with
    ?subscribed=1 anchored to #newsletter so the success state is visible
    immediately. On failure, re-renders the home page with the bound form
    so the user sees their errors and previous input.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('core:home') + '?subscribed=1#newsletter')

    # Re-render the home page with the bound form. Late import keeps the
    # apps loosely coupled — engagement doesn't import core at module level.
    from core.views import HomeView
    context = HomeView().get_context_data()
    context['subscriber_form'] = form
    return render(request, 'core/home.html', context, status=400)
