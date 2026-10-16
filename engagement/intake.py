"""
engagement/intake.py

Helpers for forwarding website form submissions to the agents system's
internal intake API (agents.islan.dev/internal/intake/).

Uses Python's stdlib urllib so no additional dependencies are needed.
Both apps are on the same droplet, so the call is effectively loopback
and should be extremely reliable.

Configuration (via islandev's .env):
    AGENTS_INTAKE_URL    Base URL for the agents intake API, e.g.
                         https://agents.islan.dev/internal
    AGENTS_INTAKE_SECRET Bearer token — must match agents' INTAKE_SECRET.
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def _post_to_agents(endpoint_path, payload):
    """
    POST a JSON payload to the agents intake API.

    Args:
        endpoint_path: path relative to AGENTS_INTAKE_URL, e.g. 'intake/prospect'.
        payload:       dict to serialise as JSON body.

    Returns:
        (True,  response_dict)  on HTTP 2xx
        (False, error_dict)     on HTTP error or connection failure
    """
    base = getattr(settings, 'AGENTS_INTAKE_URL', '').rstrip('/')
    secret = getattr(settings, 'AGENTS_INTAKE_SECRET', '')

    if not base or not secret:
        logger.error(
            'intake: AGENTS_INTAKE_URL or AGENTS_INTAKE_SECRET not configured'
        )
        return False, {'error': 'Integration not configured'}

    url = f'{base}/{endpoint_path}/'
    body = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {secret}',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            response_data = json.loads(resp.read())
            return True, response_data

    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            error_data = json.loads(raw)
        except Exception:
            error_data = {'error': exc.reason}
        logger.error(
            'intake: HTTP %d from agents endpoint %s — %s',
            exc.code, endpoint_path, error_data,
        )
        return False, error_data

    except urllib.error.URLError as exc:
        logger.error(
            'intake: connection error calling agents endpoint %s — %s',
            endpoint_path, exc.reason,
        )
        return False, {'error': str(exc.reason)}

    except Exception as exc:
        logger.exception(
            'intake: unexpected error calling agents endpoint %s', endpoint_path
        )
        return False, {'error': str(exc)}


def submit_prospect(company_name, industry, description, name, role, email):
    """
    Forward a workshop intake submission to the agents prospect endpoint.
    Returns (True, {'id': pk}) on success, (False, error_dict) on failure.
    """
    return _post_to_agents('intake/prospect', {
        'company_name': company_name,
        'industry':     industry,
        'description':  description,
        'name':         name,
        'role':         role,
        'email':        email,
    })


def submit_inquiry(name, email, message):
    """
    Forward a general contact message to the agents inquiry endpoint.
    Returns (True, {'id': pk}) on success, (False, error_dict) on failure.
    """
    return _post_to_agents('intake/inquiry', {
        'name':    name,
        'email':   email,
        'message': message,
    })
