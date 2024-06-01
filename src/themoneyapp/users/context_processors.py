"""Context processors for the themoneyapp.users application."""

from __future__ import annotations

import typing as t

from django.conf import settings
from django.http import HttpRequest


def allauth_settings(request: HttpRequest) -> dict[str, t.Any]:  # noqa: ARG001
    """Expose some settings from django-allauth in templates.

    Args:
        request (HttpRequest): client request.

    Returns:
        dict[str, t.Any]: django-allauth settings in the template context.
    """
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }
