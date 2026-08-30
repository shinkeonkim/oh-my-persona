from .base import *  # noqa

# ========== CORS / CSRF settings ==========

CORS_ALLOWED_ORIGINS = [
    "https://frontend-git-dev-yuwon.vercel.app",
    "https://kkambbaki-frontend.vercel.app",
    "https://kkambbaki.singun11.wtf",
]

CSRF_TRUSTED_ORIGINS = [
    "https://frontend-git-dev-yuwon.vercel.app",
    "https://kkambbaki-frontend.vercel.app",
    "https://kkambbaki.singun11.wtf",
]

CORS_ALLOW_CREDENTIALS = True

# 커스텀 헤더 허용 (X-BOT-TOKEN)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-bot-token",  # 커스텀 헤더 추가
]

# ========== END CORS / CSRF settings ==========

# ========== Security settings ==========

# HTTPS 사용 시 설정
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # .env에서 제어 가능
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ========== END Security settings ==========

# ========== Static & Media Files settings ==========

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (User uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========== END Static & Media Files settings ==========
