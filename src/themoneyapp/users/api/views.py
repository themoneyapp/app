"""API views for the themoneyapp.users app."""

from __future__ import annotations

import typing as t

from django.db.models.query import QuerySet
from django.http import HttpRequest

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer
from themoneyapp.users.models import User


class UserViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    GenericViewSet[User],
):
    """all drf views for the users."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args: t.Any, **kwargs: t.Any) -> QuerySet[User]:  # noqa: ANN401
        """Queryset for the current authenticated user."""
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request: HttpRequest) -> Response:
        """Details for the current authenticated user."""
        serializer = UserSerializer(request.user, context={"request": request})  # type: ignore[arg-type]
        return Response(status=status.HTTP_200_OK, data=serializer.data)
