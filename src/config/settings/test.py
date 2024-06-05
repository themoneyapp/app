"""Tests Settings."""

from .development import *  # noqa: F403
from .development import WEBPACK_LOADER


# django-webpack-loader
# ------------------------------------------------------------------------------
WEBPACK_LOADER["DEFAULT"]["LOADER_CLASS"] = "webpack_loader.loaders.FakeWebpackLoader"
