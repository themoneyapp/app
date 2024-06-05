"""themoneyapp app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TheMoneyAppConfig(AppConfig):
    """themoneyapp application and its configuration."""

    name = "themoneyapp"
    verbose_name = _("TheMoneyApp")
