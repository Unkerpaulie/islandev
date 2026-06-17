"""
Transactional email helpers for the engagement app.

All outgoing mail goes through the Resend SDK. If RESEND_API_KEY is not set
(e.g. local dev without a key) the functions log a warning and return None
instead of raising so the form submission still succeeds silently.
"""
import logging

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


def _send(*, subject: str, html: str) -> dict | None:
    """Low-level wrapper around resend.Emails.send.

    Returns the Resend response dict on success, None if the API key is absent
    or if Resend raises (logged at ERROR level so the submission is not lost).
    """
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    if not api_key:
        logger.warning('RESEND_API_KEY not set — skipping email: %s', subject)
        return None

    resend.api_key = api_key
    try:
        return resend.Emails.send({
            'from': settings.RESEND_FROM_EMAIL,
            'to': [settings.CONTACT_NOTIFICATION_EMAIL],
            'subject': subject,
            'html': html,
        })
    except Exception:
        logger.exception('Resend failed to send email: %s', subject)
        return None


def _row(label: str, value: str) -> str:
    """Render a single labelled row in the notification email body."""
    return (
        f'<tr>'
        f'<td style="padding:6px 12px;font-weight:600;color:#555;white-space:nowrap">{label}</td>'
        f'<td style="padding:6px 12px;color:#222">{value or "—"}</td>'
        f'</tr>'
    )


def _wrap_table(rows: str) -> str:
    return (
        '<table style="border-collapse:collapse;font-family:sans-serif;font-size:14px;'
        'width:100%;max-width:600px">'
        f'{rows}'
        '</table>'
    )


def send_booking_email(booking) -> dict | None:
    """Send a booking-request notification email for a BookingRequest instance."""
    rows = (
        _row('Name', booking.name)
        + _row('Email', booking.email)
        + _row('Business', booking.business_name)
        + _row('Service', booking.get_service_interest_display() if booking.service_interest else '')
        + _row('Date', str(booking.preferred_date))
        + _row('Time', booking.preferred_time.strftime('%I:%M %p') if booking.preferred_time else '')
        + _row('Message', booking.message)
    )
    html = (
        '<h2 style="font-family:sans-serif;color:#0d9488">New Booking Request</h2>'
        + _wrap_table(rows)
    )
    return _send(subject=f'New Booking Request — {booking.name}', html=html)


def send_contact_email(inquiry) -> dict | None:
    """Send a contact-inquiry notification email for a ContactInquiry instance."""
    rows = (
        _row('Name', inquiry.name)
        + _row('Email', inquiry.email)
        + _row('Company', inquiry.company)
        + _row('Message', inquiry.message)
    )
    html = (
        '<h2 style="font-family:sans-serif;color:#0d9488">New Contact Message</h2>'
        + _wrap_table(rows)
    )
    return _send(subject=f'New Contact Message — {inquiry.name}', html=html)
