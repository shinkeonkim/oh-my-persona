from pathlib import Path

import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
SERVICE_NAME = "joah_api"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

SITE_ID = 1

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

__all__ = [
  "env",
  "BASE_DIR",
  "SECRET_KEY",
  "DEBUG",
  "SERVICE_NAME",
  "WSGI_APPLICATION",
  "ASGI_APPLICATION",
  "SITE_ID",
  "DEFAULT_AUTO_FIELD",
]
