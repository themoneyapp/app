from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import pytest
from django.test import RequestFactory

from themoneyapp.users.forms import UserAdminChangeForm
from themoneyapp.users.models import User
from themoneyapp.users.tests.factories import UserFactory
from themoneyapp.users.views import user_detail_view, UserRedirectView, UserUpdateView


pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """Test user update.

    Todo:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest) -> HttpResponse:
        """Return a dummy response for the request."""
        return None  # type: ignore[return-value]

    def test_get_success_url(self, user: User, rf: RequestFactory) -> None:
        """Test the redirect url when user is successfully updated."""
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/users/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory) -> None:
        """
        Test UserUpdateView.get_object function to return the current authticated user.
        """
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory) -> None:
        """
        Test the django messages generated on successful submissions of
        UserAdminChangeForm form.
        """
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory) -> None:
        """
        Test the redirect url when `UserRedirectView.get_redirect_url` is invoked.
        """
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == reverse("themoneyapp:index")


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory) -> None:
        """
        Test that the user detail view is successfully loaded
        for an authenticated user.
        """
        request = rf.get("/fake-url/")
        request.user = UserFactory()
        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory) -> None:
        """
        Test that the user is redirected to login page when user detail view
        is requrested for an unauthenticated user.
        """
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, pk=user.pk)

        login_url = reverse(settings.LOGIN_URL)
        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"
