"""Tasks related to themoneyapp.users app."""

from django.core import management

from celery import shared_task

from .models import User
from themoneyapp.core.logger import logger


@shared_task
def clearsessions() -> None:
    """Clear user sessions."""
    logger.info("Clearing user sessions...")
    another_task.delay()
    management.call_command("clearsessions")
    logger.info("Cleared user sessions")


@shared_task
def another_task() -> None:
    """Simple task to simply log."""
    logger.info("another_task called")


@shared_task()
def get_users_count() -> int:
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()
