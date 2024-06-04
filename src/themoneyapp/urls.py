"""URLs for themoneyapp application."""

from django.urls import path

from themoneyapp.core.views import ProtectedTemplateView


app_name = "themoneyapp"

urlpatterns = [
    path(
        "",
        ProtectedTemplateView.as_view(template_name="themoneyapp/index.html"),
        name="index",
    ),
]
