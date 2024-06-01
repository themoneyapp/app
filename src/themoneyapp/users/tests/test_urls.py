from django.urls import resolve, reverse

from themoneyapp.users.models import User


def test_detail(user: User) -> None:
    """Test the user detail view url."""
    assert (
        reverse("themoneyapp_users:detail", kwargs={"pk": user.pk})
        == f"/users/{user.pk}/"
    )
    assert resolve(f"/users/{user.pk}/").view_name == "themoneyapp_users:detail"


def test_update() -> None:
    """Test the user update view url."""
    assert reverse("themoneyapp_users:update") == "/users/~update/"
    assert resolve("/users/~update/").view_name == "themoneyapp_users:update"


def test_redirect() -> None:
    """Test the user redirect view url."""
    assert reverse("themoneyapp_users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "themoneyapp_users:redirect"
