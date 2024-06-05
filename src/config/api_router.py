"""API urls for themoneyapp."""

from __future__ import annotations

import typing as t

from django.conf import settings
from django.urls import include, path, URLPattern, URLResolver

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.versioning import URLPathVersioning

from themoneyapp.users.api.views import UserViewSet


app_name = "api"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

v1_urlpatterns: t.Sequence[URLPattern | URLResolver] = [
    path("", include(router.urls)),
    path(
        "schema/",
        SpectacularAPIView.as_view(versioning_class=URLPathVersioning),
        name="api-schema-v1",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            url_name="api:api-schema-v1", versioning_class=URLPathVersioning
        ),
        name="api-docs-v1",
    ),
]

# do the following add API versioning
urlpatterns = [
    # API base url
    path("v1/", include(v1_urlpatterns)),
]
