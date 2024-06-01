"""Celery app for themoneyapp project."""

import os
import sys
import typing as t

from django.apps import apps

from celery import Celery
from celery.signals import setup_logging
from django_structlog.celery.steps import DjangoStructLogInitStep

from themoneyapp.celery_beat import CELERYBEAT_SCHEDULE


settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", None)
if settings_module is None:
    print(  # noqa: T201
        "Error: no DJANGO_SETTINGS_MODULE found. Will NOT start devserver. "
        "Remember to create .env file at project root. "
        "Check README for more info."
    )
    sys.exit(1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)


app = Celery("themoneyapp_worker")

# configure celery app

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.update(CELERY_BEAT_SCHEDULE=CELERYBEAT_SCHEDULE)

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

# A step to initialize django-structlog
app.steps["worker"].add(DjangoStructLogInitStep)


# https://github.com/celery/celery/issues/2509#issuecomment-153936466
# keep this here to make sure celery doesn't touch logging config at all.
# https://docs.celeryq.dev/en/latest/userguide/signals.html#setup-logging
# Celery wont configure the loggers if this signal is connected,
# so you can use this to completely override the logging configuration with your own.
@setup_logging.connect
def celery_setup_logging(**kwargs: t.Any) -> None:  # noqa: ANN401
    """Setup logging."""
    import logging.config

    from django.conf import settings

    logging.config.dictConfigClass(settings.LOGGING).configure()  # type: ignore[misc]
    logging.info("Celery logger configured")
