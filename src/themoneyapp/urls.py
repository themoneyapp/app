"""URLs for themoneyapp application."""

from django.urls import path
from django.views.generic import TemplateView


app_name = "themoneyapp"

urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="themoneyapp/index.html"), name="index"
    ),
]
