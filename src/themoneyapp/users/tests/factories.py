import typing as t
from collections.abc import Sequence

from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from themoneyapp.users.models import User


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(
        self,
        create: bool,  # noqa: FBT001
        extracted: Sequence[t.Any],
        **kwargs: t.Any,
    ) -> None:
        """Post generation callback to set the password for a user."""
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    @classmethod
    def _after_postgeneration(
        cls,
        instance: User,
        create: bool,  # noqa: FBT001
        results: dict[str, t.Any] | None = None,
    ) -> None:
        """Save again the instance if creating and at least one hook ran.

        Hook called after post-generation declarations have been handled.

        Args:
            instance (User): the generated user instance
            create (bool): whether the strategy was 'build' or 'create'
            results (dict or None): result of post-generation declarations
        """
        if create and results and not cls._meta.skip_postgeneration_save:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()

    class Meta:
        """Meta attributes for UserFactory."""

        model = User
        django_get_or_create = ["email"]
