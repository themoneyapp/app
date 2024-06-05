from http import HTTPStatus

from django.urls import reverse

import pytest
from django.test import Client


def test_swagger_accessible_by_admin(admin_client: Client) -> None:
    """Test that swagger UI is accessible by an admin user."""
    url = reverse("api:api-docs-v1")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_swagger_ui_accessible_without_authentication(client: Client) -> None:
    """Test that swagger UI is accessible without any authentication."""
    url = reverse("api:api-docs-v1")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_api_schema_accessible_by_admin(admin_client: Client) -> None:
    """Test that swagger schema is accessible by an admin user."""
    url = reverse("api:api-schema-v1")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_api_schema_accessible_without_authentication(client: Client) -> None:
    """Test that swagger schema is accessible without any authentication."""
    url = reverse("api:api-schema-v1")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
