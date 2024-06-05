from django.urls import resolve, reverse

from themoneyapp.users.models import User


def test_user_detail(user: User) -> None:
    """Test the url for api:user-detail route."""
    assert (
        reverse("api:user-detail", kwargs={"pk": user.pk})
        == f"/api/v1/users/{user.pk}/"
    )
    assert resolve(f"/api/v1/users/{user.pk}/").view_name == "api:user-detail"


def test_user_list() -> None:
    """Test the url for api:user-list route."""
    assert reverse("api:user-list") == "/api/v1/users/"
    assert resolve("/api/v1/users/").view_name == "api:user-list"


def test_user_me() -> None:
    """Test the url for api:user-me route."""
    assert reverse("api:user-me") == "/api/v1/users/me/"
    assert resolve("/api/v1/users/me/").view_name == "api:user-me"
