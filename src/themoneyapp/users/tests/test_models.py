from themoneyapp.users.models import User


def test_user_get_absolute_url(user: User) -> None:
    """Test the url for user profile page."""
    assert user.get_absolute_url() == f"/users/{user.pk}/"
