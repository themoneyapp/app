"""Model Serializers to be used for DRF views."""

from rest_framework import serializers

from themoneyapp.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    """Serializer for the `themoneyapp_users.User` model."""

    class Meta:
        """Meta class for the UserSerializer."""

        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }
