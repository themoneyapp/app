from io import StringIO

from django.core.management import call_command

import pytest

from themoneyapp.users.models import User


@pytest.mark.django_db()
class TestUserManager:
    def test_create_user(self) -> None:
        """Test create user using our custom object manager."""
        user = User.objects.create_user(
            email="john@example.com",
            password="something-r@nd0m!",
        )
        assert user.email == "john@example.com"
        assert user.is_active is True
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password("something-r@nd0m!")
        assert user.username is None  # type: ignore[has-type]

    def test_create_superuser(self) -> None:
        """Test create superuser using our custom object manager."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="something-r@nd0m!",
        )
        assert user.email == "admin@example.com"
        assert user.is_active is True
        assert user.is_staff
        assert user.is_superuser
        assert user.username is None  # type: ignore[has-type]

    def test_create_superuser_username_ignored(self) -> None:
        """Test create user using our custom object manager with username."""
        user = User.objects.create_superuser(
            email="test@example.com",
            password="something-r@nd0m!",
            username="some-username",
        )
        assert user.username is None  # type: ignore[has-type]


@pytest.mark.django_db()
def test_createsuperuser_command() -> None:
    """Ensure createsuperuser command works with our custom manager."""
    out = StringIO()
    command_result = call_command(
        "createsuperuser",
        "--email",
        "henry@example.com",
        interactive=False,
        stdout=out,
    )

    assert command_result is None
    assert out.getvalue() == "Superuser created successfully.\n"  # type: ignore[unreachable]
    user = User.objects.get(email="henry@example.com")
    assert user.has_usable_password() is False
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True
