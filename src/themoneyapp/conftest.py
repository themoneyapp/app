"""Pytest confest."""

from pathlib import Path

import pytest
from pytest_django.fixtures import SettingsWrapper

from themoneyapp.users.models import User
from themoneyapp.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(tmp_path: Path, settings: SettingsWrapper) -> None:
    """Set the MEDIA_ROOT to a temporary directory."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture()
def user(db: None) -> User:  # noqa: ARG001
    """Fixture to create a new user."""
    return UserFactory()
