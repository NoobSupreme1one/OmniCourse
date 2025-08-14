"""
Test settings for OmniCourse project.
"""

from .base import *

# Test overrides
DEBUG = False

# Allow Django test client host
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Use in-memory database for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True

# Use in-memory email backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Use local storage for tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Celery eager execution for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Password hashers (faster for tests)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# AWS settings for tests (mock)
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"
AWS_STORAGE_BUCKET_NAME = "test-bucket"

# Bedrock settings for tests (mock)
BEDROCK_REGION = "us-east-1"
BEDROCK_MODEL_ID = "test-model"

# Permissions flags for tests
ALLOW_ANON_WRITE_FOR_TESTS = True
