from .base import *  # noqa

# ========== CORS / CSRF settings ==========

ALPHA_BASE_URL = "https://alpha.singun11.wtf"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://frontend-git-dev-yuwon.vercel.app",
    "https://kkambbaki-frontend.vercel.app",
    ALPHA_BASE_URL,
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://frontend-git-dev-yuwon.vercel.app",
    "https://kkambbaki-frontend.vercel.app",
    ALPHA_BASE_URL,
]

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

CORS_ALLOW_CREDENTIALS = True

# ========== END CORS / CSRF settings ==========
