"""
Development settings for OmniCourse project.
"""

from .base import *

# Override for development
DEBUG = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="omnicourse_dev"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Use console email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development-specific logging
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["omnicourse"]["level"] = "DEBUG"

# Django Extensions for development
INSTALLED_APPS += ["django_extensions"]

# Development media storage (local)
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Celery eager execution for development
CELERY_TASK_ALWAYS_EAGER = config("CELERY_EAGER", default=True, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

# AWS settings for development (use localstack)
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="http://localhost:4566")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="test")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="test")

# Bedrock settings for development
BEDROCK_ENDPOINT_URL = config("BEDROCK_ENDPOINT_URL", default=None)
