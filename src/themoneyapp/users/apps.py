"""themoneyapp.urers app config."""

import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TheMoneyAppUsersConfig(AppConfig):
    """themoneyapp.users application and its configuration."""

    name = "themoneyapp.users"
    label = "themoneyapp_users"
    verbose_name = _("TheMoneyApp Users")

    def ready(self) -> None:
        """Callback for when django starts."""
        with contextlib.suppress(ImportError):
            import themoneyapp.users.signals  # noqa: F401
