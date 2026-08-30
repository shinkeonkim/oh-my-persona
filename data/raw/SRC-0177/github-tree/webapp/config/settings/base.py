"""
Django settings for dionysus project.
"""

import logging
from datetime import timedelta
from typing import List

import environ
import sentry_sdk
from django.templatetags.static import static

from .logging_config import get_logging_config

# Default Environment Variables

PROJECT_DIR = environ.Path(__file__) - 4
BASE_DIR = environ.Path(__file__) - 3

env = environ.Env(DEBUG=(bool, False))

env.read_env(f"{PROJECT_DIR}/.env")
env.read_env(f"{BASE_DIR}/.env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG") == "True" or bool(env("DEBUG"))

SITE_ID = 1

# Network settings

ALLOWED_HOSTS = ["*"]

# Application definition

PRE_PACKAGE_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "corsheaders",
]

DJANGO_APPS = [
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PACKAGE_APPS = [
    "django.contrib.postgres",
    "psqlextra",
    "django_extensions",
    "nplusone.ext.django",
    "silk",
    "rest_framework",
    "drf_spectacular",
    "safedelete",
    "django_filters",
    "django_guid",
    "drf_api_logger",
    "markdownx",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.kakao",
    "allauth.socialaccount.providers.github",
    "django_celery_beat",
    "django_celery_results",
]

CUSTOM_APPS: List[str] = [
    "user",
    "bookmark",
    "meme",
    "file_manager",
    "tag",
    "api",
]

INSTALLED_APPS = PRE_PACKAGE_APPS + DJANGO_APPS + PACKAGE_APPS + CUSTOM_APPS

# Middleware settings

PRE_PACKAGE_MIDDLEWARES = [
    "corsheaders.middleware.CorsMiddleware",
    "django_guid.middleware.guid_middleware",
    "nplusone.ext.django.NPlusOneMiddleware",
    "silk.middleware.SilkyMiddleware",
]

DJANGO_MIDDLEWARES = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

PACKAGE_MIDDLEWARES = [
    "allauth.account.middleware.AccountMiddleware",
    "config.middleware.CamelCaseMiddleware",
    "drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware",
]

CUSTOM_MIDDLEWARES: List[str] = []

MIDDLEWARE = (
    PRE_PACKAGE_MIDDLEWARES
    + DJANGO_MIDDLEWARES
    + PACKAGE_MIDDLEWARES
    + CUSTOM_MIDDLEWARES
)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# User model settings

AUTH_USER_MODEL = "user.User"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ========== DRF settings ==========

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "api.shared.pagination.StandardPagePagination",
    "PAGE_SIZE": 10,
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
    "JWT_AUTH_COOKIE": "dionysus-app-auth",
    "JWT_AUTH_REFRESH_COOKIE": "dionysus-app-refresh",
    "SIGNUP_FIELDS": {"email": {"required": True}, "username": {"required": False}},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Dionysus API",
    "DESCRIPTION": "Meme Project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": "shinkeonkim",
        "email": "dev.shinkeonkim@gmail.com",
    },
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "theme": "dark",
        "validatorUrl": None,
    },
}

REST_USE_JWT = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ========== END DRF Spectacular settings ==========

# ========== Logging settings ==========

LOGGING = get_logging_config(BASE_DIR, debug=DEBUG, environment="base")
NPLUSONE_LOGGER = logging.getLogger("nplusone")
NPLUSONE_LOG_LEVEL = logging.WARN

# ========== END Logging settings ==========

# ========== drf-api-logger settings ==========

DRF_API_LOGGER_DATABASE = True

# TODO: APILogsModel에 대해 DB 인덱스를 추가하는것이 좋아보임.

DRF_LOGGER_QUEUE_MAX_SIZE = 50
DRF_LOGGER_INTERVAL = 10

DRF_API_LOGGER_SKIP_NAMESPACE: List[str] = []
DRF_API_LOGGER_SKIP_URL_NAME: List[str] = []
DRF_API_LOGGER_EXCLUDE_KEYS = [
    "password",
    "token",
    "access",
    "refresh",
]  # TODO: 보안 정보에 대한 키워드를 추가하기

DRF_API_LOGGER_DEFAULT_DATABASE = (
    "default"  # TODO: 별도 로깅을 위한 데이터베이스 설정하는게 좋아보임.
)

DRF_API_LOGGER_SLOW_API_ABOVE = (
    200  # TODO: 200ms 보다 더 빠르게 처리할 수 있는지 확인하기
)


# ========== END drf-api-logger settings ==========

# ========== Unfold settings ==========

UNFOLD = {
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/scripts.js"),
    ],
}

# ========== END Unfold settings ==========

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# ========== Silk settings ==========

SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True

# ========== END Silk settings ==========

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://alpha.memez.party",
    "https://alpha.memez.party",
    "http://memez.party",
    "https://memez.party",
    "http://www.memez.party",
    "https://www.memez.party",
    "http://meme-party-front-deploy.vercel.app",
    "https://meme-party-front-deploy.vercel.app",
]

BASE_URL = "http://localhost:8000/"
KAKAO_CALLBACK_URI = BASE_URL + "api/v1/accounts/kakao/login/callback/"

KAKAO_REST_API_KEY = env("KAKAO_REST_API_KEY", default="")
KAKAO_ADMIN_KEY = env("KAKAO_ADMIN_KEY", default="")


# ========== Sentry settings ==========

if not DEBUG:
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        traces_sample_rate=1.0,
    )

# ========== END Sentry settings ==========

# ========== Celery settings ==========

REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_PORT = env("REDIS_PORT", default="6379")
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat 설정
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ========== END Celery settings ==========
