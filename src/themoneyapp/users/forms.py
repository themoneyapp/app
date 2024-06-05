"""forms for the themoneyapp.users application."""

from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm[User]):
    """Form for User change in the Admin Area."""

    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        """Meta class for the UserAdminChangeForm form class."""

        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm[User]):
    """Form for User Creation in the Admin Area.

    To change user signup, see UserSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        """Meta class for the UserAdminCreationForm form class."""

        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """Form that will be rendered on a user sign up section/screen.

    Default fields will be added automatically.
    """
