import os
import sys
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.settings_common import *  # noqa F403
from settings.settings_common import INSTALLED_APPS
from settings.settings_common import REST_FRAMEWORK  # noqa


from settings.settings_databases import (
    LocationKey,
    get_docker_host,
    get_database_key,
    OVERRIDE_HOST_ENV_VAR,
    OVERRIDE_PORT_ENV_VAR,
)

# Application definition

INSTALLED_APPS += [
    "drf_yasg",
    "afvalcontainers",
    "kilogram",
    "enevo",
    "sidcon",
    # "crispy_forms",
]

# CRISPY_TEMPLATE_PACK = 'bootstrap4'

ROOT_URLCONF = "afvalcontainers.urls"

WSGI_APPLICATION = "afvalcontainers.wsgi.application"

DATABASE_OPTIONS = {
    LocationKey.docker: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("DATABASE_NAME", "afvalcontainers"),
        "USER": os.getenv("DATABASE_USER", "afvalcontainers"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "insecure"),
        "HOST": "database",
        "PORT": "5432",
        "CONN_MAX_AGE": 60
    },
    LocationKey.local: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("DATABASE_NAME", "afvalcontainers"),
        "USER": os.getenv("DATABASE_USER", "afvalcontainers"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "insecure"),
        "HOST": get_docker_host(),
        "PORT": "5432",
        "CONN_MAX_AGE": 60
    },
    LocationKey.override: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("DATABASE_NAME", "afvalcontainers"),
        "USER": os.getenv("DATABASE_USER", "afvalcontainers"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "insecure"),
        "HOST": os.getenv(OVERRIDE_HOST_ENV_VAR),
        "PORT": os.getenv(OVERRIDE_PORT_ENV_VAR, "5432"),
        "CONN_MAX_AGE": 60
    },
    LocationKey.kilogram: {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        # NOTE in production database is called KILOGRAM
        "NAME": os.getenv("DATABASE_KILOGRAM_NAME", "afvalcontainers"),
        "USER": os.getenv("DATABASE_KILOGRAM_USER", "afvalcontainers"),
        "PASSWORD": os.getenv("DATABASE_KILOGRAM_PASSWORD", "insecure"),
        "HOST": os.getenv('DATABASE_KILOGRAM_HOST', "database"),
        "PORT": os.getenv('DATABASE_KILOGRAM_PORT', "5432"),
    },
}

# Database
DATABASES = {
    "default": DATABASE_OPTIONS[get_database_key()],
    "kilogram": DATABASE_OPTIONS['kilogram']
}

TESTING = False
if 'test' in sys.argv:
    # during test we do not need kilogram database
    TESTING = True
    DATABASES.pop('kilogram')


STATIC_URL = '/afval/static/'
STATIC_ROOT = '/static/'


HEALTH_MODEL = "afvalcontainers.Container"

# The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256   # noqa
# This is a test public/private key def and added for testing .
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""

DATAPUNT_AUTHZ = {"JWKS": os.getenv("PUB_JWKS", JWKS_TEST_KEY)}


WASTE_DESCRIPTIONS = (
    ("Rest"),
    ("Glas"),
    ("Papier"),
    ("Textiel"),
    ("GFT"),
    ("Glas"),
    ("KCA"),
    ("Plastic"),
    ("Kunstof"),
    ("Grof"),
)

STADSDELEN = (
    ("B", "Westpoort (B)"),
    ("M", "Oost (M)"),
    ("N", "Noord (N)"),
    ("A", "Centrum (A)"),
    ("E", "West (E)"),
    ("F", "Nieuw-West (F)"),
    ("K", "Zuid (K)"),
    ("T", "Zuidoost (T)"),
)

WASTE_CHOICES = [(w, w) for w in WASTE_DESCRIPTIONS]

SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
