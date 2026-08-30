from .base import *  # noqa

ENVIRONMENT = "production"
BASE_URL = env.str("BASE_URL", default="https://joah.singun11.wtf")
DEBUG = False
ADMIN_SITE_URL = BASE_URL + "admin/"

# ========== CORS / CSRF settings ==========

CORS_ALLOWED_ORIGINS = [
  # TODO: 배포 후 도메인 설정
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost:8000",
  "https://localhost:8000",
  "http://app:8000",
  "https://app:8000",
  "http://joah.singun11.wtf",
  "https://joah.singun11.wtf",
]

CSRF_TRUSTED_ORIGINS = [
  # TODO: 배포 후 도메인 설정
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost:8000",
  "https://localhost:8000",
  "http://app:8000",
  "https://app:8000",
  "http://joah.singun11.wtf",
  "https://joah.singun11.wtf",
]

# HTTPS 강제
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# 쿠키 보안
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_CIDR_NETS = ["192.168.0.0/16"]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"
