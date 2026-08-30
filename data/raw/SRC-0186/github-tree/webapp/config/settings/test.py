from .base import *  # noqa: F401, F403

ENVIRONMENT = env.str("ENVIRONMENT", default="test")
PORT = env("PORT", default=8000)
BASE_URL = env("BASE_URL", default=f"http://localhost:{PORT}/").rstrip()

ALLOWED_HOSTS = ["*"]
DEBUG = True

ADMIN_SITE_URL = BASE_URL + "admin/"

DATABASES["default"]["NAME"] = TEST_POSTGRES_DB
DATABASES["default"]["USER"] = TEST_POSTGRES_USER
DATABASES["default"]["PASSWORD"] = TEST_POSTGRES_PASSWORD
DATABASES["default"]["HOST"] = TEST_POSTGRES_HOST
DATABASES["default"]["PORT"] = TEST_POSTGRES_PORT

# ========== Celery settings for tests ==========

# Use in-memory broker for tests to avoid Redis dependency
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Disable Celery Beat scheduler for tests
CELERY_BEAT_SCHEDULER = None

# ========== END Celery settings for tests ==========
