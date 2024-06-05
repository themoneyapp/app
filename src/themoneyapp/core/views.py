"""Generic django views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProtectedTemplateView(LoginRequiredMixin, TemplateView):
    """Template view which requires an authenticated user."""
