from .base import *  # noqa: F401, F403

PORT = env("PORT", default=8000)
ALLOWED_HOSTS = ["*"]
DEBUG = True

# ========== Celery settings for tests ==========

# Use in-memory broker for tests to avoid Redis dependency
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Disable Celery Beat scheduler for tests
CELERY_BEAT_SCHEDULER = None

# ========== END Celery settings for tests ==========
