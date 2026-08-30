from .base import *  # noqa: F401, F403

ENVIRONMENT = env.str("ENVIRONMENT", default="development")
PORT = env("PORT", default=8000)
BASE_URL = env("BASE_URL", default=f"http://localhost:{PORT}/")
FRONT_BASE_URL = env.str("FRONT_BASE_URL", default="http://localhost:3000")

# CSRF trusted origins for nginx proxy
CSRF_TRUSTED_ORIGINS = [
  "http://localhost:8000",
  "http://127.0.0.1:8000",
  "http://localhost:3000",
  "http://0.0.0.0:3000",
]
# CORS 설정 - 프론트엔드 도메인 허용
CORS_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://0.0.0.0:3000",
]

KAKAO_CALLBACK_URI = env("KAKAO_CALLBACK_URI", default="http://localhost:3000/auth/callback")  # TODO: 프론트엔드 작업 후 수정
KAKAO_TEST_CALLBACK_URI = BASE_URL + "api/v1/users/kakao/test/callback/"
ADMIN_SITE_URL = BASE_URL + "admin/"
