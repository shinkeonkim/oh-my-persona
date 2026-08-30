from .base import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": "localhost",
        "PORT": env("POSTGRES_PORT"),
    }
}

# ========== Celery settings for tests ==========

# Use in-memory broker for tests to avoid Redis dependency
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Disable Celery Beat scheduler for tests
CELERY_BEAT_SCHEDULER = None

# ========== END Celery settings for tests ==========

# ========== Test-specific optimizations ==========

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for faster test database setup
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# Uncomment the line below if you want to disable migrations for faster tests
# MIGRATION_MODULES = DisableMigrations()

# ========== END Test-specific optimizations ==========

# Static files (CSS, JavaScript, Images)

STATIC_DIR = f"{BASE_DIR}/static"
STATIC_ROOT = f"{BASE_DIR}/static"
STATIC_URL = "/static/"

# Media files
MEDIA_ROOT = f"{BASE_DIR}/media"
MEDIA_URL = "media/"

# ========== Logging settings ==========

LOGGING = get_logging_config(BASE_DIR, debug=DEBUG, environment="test")

# ========== END Logging settings ==========
