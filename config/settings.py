"""
Django settings for the funky-lobsters project.

12-factor: every secret and every environment-specific value comes from an
environment variable. Locally these are read from a `.env` file (never committed;
copy `.env.example`). On Render they are set in the dashboard / render.yaml.
"""

import os
import sys
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a local .env file if there is one (local development only).
load_dotenv(BASE_DIR / ".env")

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


# --- Core security settings ---------------------------------------------------

DEBUG = env_bool("DEBUG", default=False)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG or TESTING:
        SECRET_KEY = "django-insecure-local-development-only"
    else:
        raise ImproperlyConfigured("SECRET_KEY environment variable is not set.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Render sets this automatically to the app's public hostname, e.g. funky-lobsters-staging.onrender.com
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

if not DEBUG and not TESTING:
    # Render terminates HTTPS in front of the app and tells us via this header.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# --- Applications ---------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "core",
    "abtest",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Database ---------------------------------------------------------------------
# The app always uses Postgres via DATABASE_URL (Neon dev DB locally, Neon staging DB on Render).
# Tests use a throwaway SQLite database unless TEST_DATABASE_URL is set.

if TESTING:
    test_url = os.environ.get("TEST_DATABASE_URL")
    DATABASES = {
        "default": dj_database_url.parse(test_url)
        if test_url
        else {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    }
else:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ImproperlyConfigured(
            "DATABASE_URL is not set. Copy .env.example to .env and paste your Neon "
            "dev connection string into it (see README.md)."
        )
    DATABASES = {
        "default": dj_database_url.parse(
            database_url, conn_max_age=600, conn_health_checks=True
        )
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Authentication ---------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"  # login is by email, see accounts/models.py

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"


# --- Internationalization ---------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, images) ------------------------------------
# Collected into staticfiles/ at build time and served by WhiteNoise.

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Locally and in tests, serve static files straight from the app folders (no collectstatic needed).
WHITENOISE_AUTOREFRESH = DEBUG or TESTING
WHITENOISE_USE_FINDERS = DEBUG or TESTING
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if (DEBUG or TESTING)
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}


# --- Logging: everything goes to stdout (12-factor) ----------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}
