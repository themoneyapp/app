"""Views for the themoneyapp.users application."""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from themoneyapp.users.models import User


class UserDetailView(LoginRequiredMixin, DetailView[User]):
    """View for user details."""

    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):  # type: ignore[type-arg]
    """View to update the user."""

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        """Return the URL to redirect to after processing a valid form.

        Returns:
            str: url for the user detail view.
        """
        # for mypy to know that the user is authenticated
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self) -> User | AnonymousUser:  # type: ignore[override]
        """Get the current user to update.

        Returns:
            User | AnonymousUser: current authenticated/anonymous user.
        """
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """View to redirect user on success login."""

    permanent = False

    def get_redirect_url(self) -> str:
        """Get the url to redirect to.

        Returns:
            str: URL for the index page of themoneyapp application.
        """
        return reverse("themoneyapp:index")


user_redirect_view = UserRedirectView.as_view()
