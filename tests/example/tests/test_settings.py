import os
from distutils.version import LooseVersion

from django import get_version

django_version = get_version()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

LANGUAGES = (("en", "English"),)

LANGUAGE_CODE = "en"

USE_TZ = False
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "password_policies",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "tests", "db.sqlite3"),
    }
}

LOGIN_URL = "/admin/login/"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "tests.example.urls"

SITE_ID = 1

# This is to maintain compatibility with Django 1.7
if LooseVersion(django_version) < LooseVersion("1.8.0"):
    TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), "templates"),)
    TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.contrib.messages.context_processors.messages",
        "password_policies.context_processors.password_status",
    )

else:
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                os.path.join(BASE_DIR, "templates"),
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.contrib.messages.context_processors.messages",
                    "password_policies.context_processors.password_status",
                ],
            },
        },
    ]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"


MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "password_policies.middleware.PasswordChangeMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

MEDIA_URL = "/media/somewhere/"
