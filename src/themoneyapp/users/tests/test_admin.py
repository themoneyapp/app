import contextlib
from http import HTTPStatus
from importlib import reload

from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

import pytest
from django.test import Client, RequestFactory
from pytest_django.asserts import assertRedirects
from pytest_django.fixtures import SettingsWrapper

from themoneyapp.users.models import User


class TestUserAdmin:
    def test_changelist(self, admin_client: Client) -> None:
        """
        Test the users list view is loaded successfully by an admin user.
        """
        url = reverse("admin:themoneyapp_users_user_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_search(self, admin_client: Client) -> None:
        """
        Test the users list view with a search query is loaded successfully
        by an admin user.
        """
        url = reverse("admin:themoneyapp_users_user_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == HTTPStatus.OK

    def test_add(self, admin_client: Client) -> None:
        """
        Test that the create user view in the admin app is processed successfully.
        """
        url = reverse("admin:themoneyapp_users_user_add")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

        response = admin_client.post(
            url,
            data={
                "email": "new-admin@example.com",
                "password1": "My_R@ndom-P@ssw0rd",
                "password2": "My_R@ndom-P@ssw0rd",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert User.objects.filter(email="new-admin@example.com").exists()

    def test_view_user(self, admin_client: Client) -> None:
        """
        Test the user edit view is loaded successfully by an admin user.
        """
        user = User.objects.get(email="admin@example.com")
        url = reverse(
            "admin:themoneyapp_users_user_change", kwargs={"object_id": user.pk}
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.fixture()
    def _force_allauth(self, settings: SettingsWrapper) -> None:
        """
        Reload the django admin app with DJANGO_ADMIN_FORCE_ALLAUTH=True.

        this will force the djano admin auth to be handled by django-allauth.
        """
        settings.DJANGO_ADMIN_FORCE_ALLAUTH = True
        # Reload the admin module to apply the setting change
        import themoneyapp.users.admin as users_admin

        with contextlib.suppress(admin.sites.AlreadyRegistered):  # type: ignore[attr-defined]
            reload(users_admin)

    @pytest.mark.django_db()
    @pytest.mark.usefixtures("_force_allauth")
    def test_allauth_login(self, rf: RequestFactory, settings: SettingsWrapper) -> None:
        """Test that admin auth is handled by django-allath."""
        request = rf.get("/fake-url")
        request.user = AnonymousUser()
        response = admin.site.login(request)

        # The `admin` login view should redirect to the `allauth` login view
        target_url = reverse(settings.LOGIN_URL) + "?next=" + request.path
        assertRedirects(response, target_url, fetch_redirect_response=False)
