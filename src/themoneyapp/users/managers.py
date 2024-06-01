"""managers for themoneyapp.users models."""

from __future__ import annotations

import typing as t

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

from themoneyapp.core.logger import logger


if t.TYPE_CHECKING:
    from .models import User


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: t.Any,  # noqa: ANN401
    ) -> User:
        """Internal util to create a user record.

        Create and save a user with the given email and password.

        Args:
            email (str): email address of the user
            password (str | None, optional): plaintext password. Defaults to None.
            **extra_fields (t.Any): extra args accepted by `._create_user`.

        Raises:
            ValueError: The given email must be set.

        Returns:
            User: A user instance
        """
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)

        # ignore the username field
        username = extra_fields.pop("username", None)
        if username is not None:
            logger.warning("`username` field in a user account is not supported.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(  # type: ignore[override]
        self,
        email: str,
        password: str | None = None,
        **extra_fields: t.Any,  # noqa: ANN401
    ) -> User:
        """Create a user record.

        Args:
            email (str): email address of the user
            password (str | None, optional): plaintext password. Defaults to None.
            **extra_fields (t.Any): extra args accepted by `._create_user`.

        Returns:
            User: A user instance
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(  # type: ignore[override]
        self,
        email: str,
        password: str | None = None,
        **extra_fields: t.Any,  # noqa: ANN401
    ) -> User:
        """Create a superuser record.

        Args:
            email (str): email address of the user
            password (str | None, optional): plaintext password. Defaults to None.
            **extra_fields (t.Any): extra args accepted by `.create_user`.

        Raises:
            ValueError: Superuser must have is_staff=True.
            ValueError: Superuser must have is_superuser=True.

        Returns:
            User: A user instance
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)

        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(email, password, **extra_fields)
