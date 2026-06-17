from datetime import date, timedelta

from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse

from .email import send_booking_email, send_contact_email
from .forms import BookingRequestForm, ContactInquiryForm, SubscriberForm
from .models import BookingRequest, ContactInquiry


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


def _contact_context(booking_form=None, contact_form=None, initial_mode='book', success=''):
    """Build the shared context dict for GET and error-state POST renders."""
    return {
        'booking_form': booking_form or BookingRequestForm(),
        'contact_form': contact_form or ContactInquiryForm(),
        'time_slots': TIME_SLOTS,
        'dates': _next_n_weekdays(),
        'service_choices': BookingRequest.ServiceInterest.choices,
        'initial_mode': initial_mode,
        'success': success,
    }


def contact(request):
    """Unified contact/booking page.

    GET  ?mode=book  → toggle defaults to booking mode (shows date/time fields).
    GET  (no param)  → toggle defaults to contact/message mode.

    POST mode=booking → validates BookingRequestForm, saves BookingRequest, sends email.
    POST mode=contact → validates ContactInquiryForm, saves ContactInquiry, sends email.

    On success, redirects back with ?success=<mode> so Alpine can show the
    confirmation state without re-submitting on refresh.
    """
    if request.method == 'POST':
        mode = request.POST.get('mode', 'contact')

        if mode == 'booking':
            form = BookingRequestForm(request.POST)
            if form.is_valid():
                booking = form.save()
                send_booking_email(booking)
                return redirect(
                    reverse('engagement:contact') + '?success=booking#contact'
                )
            return render(request, 'engagement/contact.html',
                          _contact_context(booking_form=form, initial_mode='book'),
                          status=400)

        else:  # mode == 'contact'
            form = ContactInquiryForm(request.POST)
            if form.is_valid():
                inquiry = form.save(commit=False)
                inquiry.inquiry_type = ContactInquiry.InquiryType.CLIENT
                inquiry.save()
                send_contact_email(inquiry)
                return redirect(
                    reverse('engagement:contact') + '?success=contact#contact'
                )
            return render(request, 'engagement/contact.html',
                          _contact_context(contact_form=form, initial_mode='contact'),
                          status=400)

    # GET — determine initial toggle state from ?mode=book
    success = request.GET.get('success', '')
    if success not in ('booking', 'contact'):
        success = ''

    raw_mode = request.GET.get('mode', '')
    initial_mode = 'book' if raw_mode == 'book' else 'contact'

    # After a successful booking keep the toggle on the booking side so the
    # success message makes visual sense.
    if success == 'booking':
        initial_mode = 'book'
    elif success == 'contact':
        initial_mode = 'contact'

    return render(request, 'engagement/contact.html',
                  _contact_context(initial_mode=initial_mode, success=success))


def book(request):
    """Legacy /book/ URL — redirect to the unified contact page in booking mode."""
    return redirect(reverse('engagement:contact') + '?mode=book')


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
