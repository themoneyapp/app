"""Production Settings."""

from __future__ import annotations

from ._base import *  # noqa: F403
from ._base import BaseAppSettings, REDIS_URL, SPECTACULAR_SETTINGS


class ProductionAppSettings(BaseAppSettings):
    """App settings read from environment for production."""

    DOMAIN_NAME: str
    SECURE_HSTS_SECONDS: int = 3600
    SECURE_SSL_REDIRECT: bool = True


# ENVIRONMENT
# ------------------------------------------------------------------------------
production_settings = ProductionAppSettings()


# GENERAL
# ------------------------------------------------------------------------------
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    production_settings.DOMAIN_NAME,
]


# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        # https://github.com/jazzband/django-redis
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
}


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/5.0/topics/security/

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = production_settings.SECURE_SSL_REDIRECT
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO:  # noqa: TD002,FIX002,TD003
# set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = production_settings.SECURE_HSTS_SECONDS
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = True
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
# https://github.com/DmytroLitvinov/django-http-referrer-policy
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
REFERRER_POLICY = "same-origin"


# STATIC & MEDIA
# ------------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# django-rest-framework
# -------------------------------------------------------------------------------
# Tools that generate code samples can use SERVERS to point to the correct domain
SPECTACULAR_SETTINGS["SERVERS"] = [
    {
        "url": f"http{'s' if SECURE_SSL_REDIRECT else ''}://{production_settings.DOMAIN_NAME}",
        "description": "Production server",
    },
]


# Your stuff...
# ------------------------------------------------------------------------------
