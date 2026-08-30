from .base import *  # noqa: F401, F403

ENVIRONMENT = env.str("ENVIRONMENT", default="production")
BASE_URL = env.str("BASE_URL", default="https://api.palette.me.kr/")
DEBUG = False
FRONT_BASE_URL = env.str("FRONT_BASE_URL", default="https://palette.me.kr")

KAKAO_CALLBACK_URI = env.str("KAKAO_CALLBACK_URI", default=" https://palette.me.kr/oauth/callback/kakao")
KAKAO_TEST_CALLBACK_URI = BASE_URL + "api/v1/users/kakao/test/callback/"
ADMIN_SITE_URL = BASE_URL + "admin/"

# ==================================================
# CloudFront 설정
# ==================================================

AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN", default="")
AWS_CLOUDFRONT_STATIC_DOMAIN = env.str("AWS_CLOUDFRONT_STATIC_DOMAIN", default=AWS_S3_CUSTOM_DOMAIN)

# ==================================================
# 보안 설정
# ==================================================

# HTTPS 강제
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS 설정
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 쿠키 보안
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_CIDR_NETS = ["192.168.0.0/16"]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

CSRF_TRUSTED_ORIGINS = [
  "http://localhost:8000",
  "https://localhost:8000",
  "http://app:8000",
  "https://app:8000",
  "https://api.palette.me.kr",
  "https://palette.me.kr",
  "https://www.palette.me.kr",
]

# CORS 설정 - 프론트엔드 도메인 허용
CORS_ALLOWED_ORIGINS = [
  "https://api.palette.me.kr",
  "https://palette.me.kr",
  "https://www.palette.me.kr",
  "https://" + AWS_S3_CUSTOM_DOMAIN,
  "https://" + AWS_CLOUDFRONT_STATIC_DOMAIN,
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # 보안을 위해 False로 설정

# ==================================================
# S3 & CloudFront 설정
# ==================================================

# AWS 설정
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env.str("AWS_REGION", default="ap-northeast-2")

# S3 보안 설정
AWS_S3_FILE_OVERWRITE = False  # 같은 이름 파일 덮어쓰기 방지
AWS_DEFAULT_ACL = None  # Bucket의 ACL 정책 사용
AWS_S3_OBJECT_PARAMETERS = {
  "CacheControl": "max-age=86400",  # 1일 캐싱
}

# Django Storages 설정
STORAGES = {
  "default": {
    "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    "OPTIONS": {
      "bucket_name": AWS_STORAGE_BUCKET_NAME,
      "region_name": AWS_S3_REGION_NAME,
      "custom_domain": AWS_S3_CUSTOM_DOMAIN,
      "file_overwrite": AWS_S3_FILE_OVERWRITE,
      "default_acl": AWS_DEFAULT_ACL,
      "object_parameters": AWS_S3_OBJECT_PARAMETERS,
    },
  },
  "staticfiles": {
    "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    "OPTIONS": {
      "bucket_name": env.str("AWS_STATIC_BUCKET_NAME", default=AWS_STORAGE_BUCKET_NAME),
      "region_name": AWS_S3_REGION_NAME,
      "custom_domain": env.str("AWS_CLOUDFRONT_STATIC_DOMAIN", default=AWS_S3_CUSTOM_DOMAIN),
      "default_acl": AWS_DEFAULT_ACL,
      "object_parameters": {
        "CacheControl": "max-age=2592000",  # 30일 캐싱
        "ContentDisposition": "inline",
      },
    },
  },
}

# URL 설정
STATIC_URL = AWS_CLOUDFRONT_STATIC_DOMAIN + "/"
MEDIA_URL = AWS_S3_CUSTOM_DOMAIN + "/"

# ==================================================
# 데이터베이스 설정 (Production)
# ==================================================

DATABASES = {
  "default": {
    "ENGINE": "psqlextra.backend",
    "NAME": env.str("POSTGRES_DB"),
    "USER": env.str("POSTGRES_USER"),
    "PASSWORD": env.str("POSTGRES_PASSWORD"),
    "HOST": env.str("POSTGRES_HOST"),
    "PORT": env.str("POSTGRES_PORT", default="5432"),
    "ATOMIC_REQUESTS": True,
    "CONN_MAX_AGE": 600,  # 10분 connection pooling
    "OPTIONS": {
      "connect_timeout": 10,
      "options": "-c statement_timeout=30000",  # 30초 쿼리 타임아웃
    },
  }
}
