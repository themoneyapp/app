from rest_framework.test import APIRequestFactory

import pytest

from themoneyapp.users.api.views import UserViewSet
from themoneyapp.users.models import User


@pytest.fixture()
def api_rf() -> APIRequestFactory:
    """Fixture to return a `APIRequestFactory` instance."""
    return APIRequestFactory()


class TestUserViewSet:
    def test_get_queryset(self, user: User, api_rf: APIRequestFactory) -> None:
        """Test queryset to check it returns the currently authenticated user."""
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory) -> None:
        """Test `me` endpoint that returns the currently authticated user."""
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg, arg-type, misc]

        assert response.data == {
            "url": f"http://testserver/api/v1/users/{user.pk}/",
            "name": user.name,
        }
