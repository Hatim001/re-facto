"""
Django settings for core project.

This module contains the settings for the Django project.
"""

import os
import sys
from pathlib import Path

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Environment of the application
APP_ENV = env("APP_ENVIRONMENT")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG") if APP_ENV != "PRODUCTION" else False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = [env("ALLOWED_HOST")]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # plugins
    "corsheaders",
    "rest_framework",
    # "django_nose",
    # apps
    "account",
    "service",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # custom middlewares
    "core.middlewares.ErrorReportingMiddleware",
]

REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema"}

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env(f"{APP_ENV}_DB_NAME"),
        "USER": env(f"{APP_ENV}_DB_USER"),
        "PASSWORD": env(f"{APP_ENV}_DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

if "test" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "TEST_CSCI5308_DB",
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# GitHub settings
GITHUB_SECRET = env("GH_SECRET")
GITHUB_AUTH = env("GH_AUTH")
GITHUB_CLIENT_ID = env("GITHUB_CLIENT_ID")
GITHUB_APP_SECRET = env("GITHUB_SECRET")

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "https://re-facto.netlify.app",
)

CORS_ALLOW_HEADERS = [
    "access-control-allow-headers",
    "access-control-allow-origin",
    "access-control-allow-methods",
    "content-type",
    "x-csrftoken",
]

# Session variables
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_AGE = 60 * 60 * 7  # keep session valid for 7 hours
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"
SESSION_EXPIRY = 60 * 60 * 7

# Python requests
REQUEST_TIMEOUT = 60

# OpenAI API key
OPENAI_API_KEY = env("OPENAI_API_KEY")

# GitHub author name and email
GITHUB_AUTHOR_NAME = "re-factor"
GITHUB_AUTHOR_EMAIL = "refactor1010@gmail.com"