from .base import *  # noqa: F401, F403

ENVIRONMENT = env.str("ENVIRONMENT", default="alpha")
PORT = env.int("PORT", default=8000)
BASE_URL = env.str("BASE_URL", default=f"http://localhost:{PORT}/")
FRONT_BASE_URL = env.str("FRONT_BASE_URL", default="https://palette-fe-flax.vercel.app/")

# Alpha environment specific settings
DEBUG = False

KAKAO_CALLBACK_URI = env.str("KAKAO_CALLBACK_URI", default=" http://localhost:3000/oauth/callback/kakao")
KAKAO_TEST_CALLBACK_URI = BASE_URL + "api/v1/users/kakao/test/callback/"
ADMIN_SITE_URL = BASE_URL + "admin/"

# Static files configuration for production-like environment
STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

# Security settings for alpha environment
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

# CSRF trusted origins for nginx proxy
CSRF_TRUSTED_ORIGINS = [
  "http://localhost:8000",
  "https://localhost:8000",
  "http://app:8000",
  "https://app:8000",
  "https://api.singun11.wtf",  # 개발용 서버
  "http://api.singun11.wtf",  # 개발용 서버
  "https://palette-fe-flax.vercel.app",
  "http://infosungui-macbookpro.local:3000",
]

# CORS 설정 - 프론트엔드 도메인 허용
CORS_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://0.0.0.0:3000",
  "http://infosungui-macbookpro.local:3000",
  "https://palette-fe-flax.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # 보안을 위해 False로 설정

ALLOWED_CIDR_NETS = ["192.168.0.0/16"]

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=1)
