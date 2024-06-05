"""Celery Beat config for the themoneyapp project."""

from celery.schedules import crontab


__all__ = ("CELERYBEAT_SCHEDULE",)


CELERYBEAT_SCHEDULE = {
    # Internal tasks
    "clearsessions": {
        "schedule": crontab(),
        "task": "themoneyapp.users.tasks.clearsessions",
    },
}
