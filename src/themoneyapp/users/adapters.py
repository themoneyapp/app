"""django-allauth adapaters for the themoneyapp application."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """The adapter class for allauth.account funcationality."""

    def is_open_for_signup(self, request: HttpRequest) -> bool:  # noqa: ARG002
        """Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        Args:
            request (HttpRequest): client request.

        Returns:
            bool: whether to allow signups.
        """
        return settings.ACCOUNT_ALLOW_REGISTRATION
