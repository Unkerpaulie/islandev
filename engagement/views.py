import logging

from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactMessageForm, SubscriberForm, WorkshopIntakeForm
from .intake import submit_inquiry, submit_prospect

logger = logging.getLogger(__name__)


def _form_context(workshop_form=None, contact_form=None,
                  initial_mode='workshop', submission_error=False):
    """Build the shared context dict for GET and error-state POST renders."""
    return {
        'workshop_form':    workshop_form or WorkshopIntakeForm(),
        'contact_form':     contact_form or ContactMessageForm(),
        'initial_mode':     initial_mode,
        'submission_error': submission_error,
    }


def contact(request):
    """
    Unified contact page with two modes:

    GET  ?mode=workshop  →  toggle opens on the workshop intake side.
    GET  (no param)      →  toggle opens on the message side.

    POST mode=workshop   →  validates WorkshopIntakeForm, forwards to agents
                            prospect endpoint, redirects to ?success=workshop.
    POST mode=contact    →  validates ContactMessageForm, forwards to agents
                            inquiry endpoint, redirects to ?success=contact.

    On agents endpoint failure the form is re-rendered with submission_error=True
    so the user sees their input and a helpful error message.
    """
    if request.method == 'POST':
        mode = request.POST.get('mode', 'contact')

        if mode == 'workshop':
            form = WorkshopIntakeForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ok, result = submit_prospect(
                    company_name=cd['company_name'],
                    industry=cd.get('industry', ''),
                    description=cd.get('description', ''),
                    name=cd['name'],
                    role=cd.get('role', ''),
                    email=cd['email'],
                )
                if ok:
                    return redirect(
                        reverse('engagement:contact') + '?success=workshop#contact'
                    )
                # agents endpoint failed — keep the form filled, show error banner
                logger.error(
                    'contact/workshop: agents endpoint failed for %s — %s',
                    cd.get('email'), result,
                )
                return render(
                    request, 'engagement/contact.html',
                    _form_context(workshop_form=form, initial_mode='workshop',
                                  submission_error=True),
                    status=500,
                )
            # Form validation errors
            return render(
                request, 'engagement/contact.html',
                _form_context(workshop_form=form, initial_mode='workshop'),
                status=400,
            )

        else:  # mode == 'contact'
            form = ContactMessageForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ok, result = submit_inquiry(
                    name=cd['name'],
                    email=cd['email'],
                    message=cd['message'],
                )
                if ok:
                    return redirect(
                        reverse('engagement:contact') + '?success=contact#contact'
                    )
                logger.error(
                    'contact/inquiry: agents endpoint failed for %s — %s',
                    cd.get('email'), result,
                )
                return render(
                    request, 'engagement/contact.html',
                    _form_context(contact_form=form, initial_mode='contact',
                                  submission_error=True),
                    status=500,
                )
            return render(
                request, 'engagement/contact.html',
                _form_context(contact_form=form, initial_mode='contact'),
                status=400,
            )

    # GET — determine initial toggle state.
    success = request.GET.get('success', '')
    if success not in ('workshop', 'contact'):
        success = ''

    raw_mode = request.GET.get('mode', '')
    if success == 'workshop' or raw_mode == 'workshop':
        initial_mode = 'workshop'
    else:
        initial_mode = 'contact'

    ctx = _form_context(initial_mode=initial_mode)
    ctx['success'] = success
    return render(request, 'engagement/contact.html', ctx)


def subscribe(request):
    """
    Handle the homepage newsletter signup.

    Accepts POST only. On success, redirects to home ?subscribed=1#newsletter.
    On failure, re-renders the home page with the bound form and errors.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('core:home') + '?subscribed=1#newsletter')

    from core.views import HomeView
    context = HomeView().get_context_data()
    context['subscriber_form'] = form
    return render(request, 'core/home.html', context, status=400)
