from datetime import timedelta

from .common import SECRET_KEY, env

AUTH_USER_MODEL = "users.User"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

SECRET_SIGNING_KEY = env.str(
  "SECRET_SIGNING_KEY",
  default=SECRET_KEY,
)
KAKAO_CALLBACK_URI = env.str(
  "KAKAO_CALLBACK_URI",
  default="http://localhost:8000/api/v1/users/kakao/callback/",
)
KAKAO_TEST_CALLBACK_URI = env.str(
  "KAKAO_TEST_CALLBACK_URI",
  default="http://localhost:8000/api/v1/users/kakao/test/callback/",
)
GOOGLE_CALLBACK_URI = env.str(
  "GOOGLE_CALLBACK_URI",
  default="http://localhost:8000/api/v1/users/google/callback/",
)
GOOGLE_TEST_CALLBACK_URI = env.str(
  "GOOGLE_TEST_CALLBACK_URI",
  default="http://localhost:8000/api/v1/users/google/test/callback/",
)

REST_AUTH = {
  "USE_JWT": True,
  "JWT_AUTH_HTTPONLY": False,
  "JWT_SERIALIZER": "api.v1.users.serializers.JWTSerializer",
  "SESSION_LOGIN": False,  # Disable session-based login for API
  "USER_DETAILS_SERIALIZER": "api.v1.users.serializers.UserDetailSerializer",
}

REST_USE_JWT = True

# Django-allauth Account Settings
ACCOUNT_AUTHENTICATION_METHOD = "email"  # Use email for authentication
ACCOUNT_EMAIL_REQUIRED = True  # Email is required
ACCOUNT_USERNAME_REQUIRED = True  # Username is required (our User model has username)
ACCOUNT_EMAIL_VERIFICATION = "none"  # Disable email verification (can change to "mandatory" in production)
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_UNIQUE_EMAIL = True  # Ensure email uniqueness

# Social Account Settings
SOCIALACCOUNT_AUTO_SIGNUP = True  # Automatically create account on social login
SOCIALACCOUNT_EMAIL_AUTHENTICATION = False  # Don't auto-connect accounts by email (security)
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = False  # Don't auto-connect on email match
SOCIALACCOUNT_EMAIL_REQUIRED = True  # Require email from social providers
SOCIALACCOUNT_QUERY_EMAIL = True  # Request email from providers
SOCIALACCOUNT_STORE_TOKENS = False  # Store OAuth tokens in database (useful for API calls)

# OAuth Provider Configurations
# Note: Provider credentials can be configured via environment variables or Django admin
KAKAO_CLIENT_ID = env.str("KAKAO_CLIENT_ID", default="")
KAKAO_SECRET_KEY = env.str("KAKAO_SECRET_KEY", default="")
GOOGLE_CLIENT_ID = env.str("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env.str("GOOGLE_CLIENT_SECRET", default="")

SOCIALACCOUNT_PROVIDERS = {
  "kakao": {
    "APPS": [{
      "client_id": KAKAO_CLIENT_ID,
      "secret": KAKAO_SECRET_KEY,
      "key": "",  # Not used by Kakao
    }],
    "SCOPE": [
      "profile_nickname",
      "profile_image",
      "account_email",
    ],
    "AUTH_PARAMS": {
      "access_type": "offline",  # Request offline access
    },
    "VERIFIED_EMAIL": False,  # Kakao email verification is optional
  },
  "google": {
    "APPS": [
      {
        "client_id": GOOGLE_CLIENT_ID,
        "secret": GOOGLE_CLIENT_SECRET,
        "key": "",  # Not used by Google
      },
    ],
    "SCOPE": [
      "profile",
      "email",
      "openid",
    ],
    "AUTH_PARAMS": {
      "access_type": "offline",  # Request offline access for refresh tokens
      "prompt": "consent",  # Force consent screen to get refresh token
    },
    "VERIFIED_EMAIL": True,  # Google verifies emails
  },
}

SIMPLE_JWT = {
  "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
  "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
  "ROTATE_REFRESH_TOKENS": True,
  "BLACKLIST_AFTER_ROTATION": True,
  "UPDATE_LAST_LOGIN": False,
  "ALGORITHM": "HS256",
  "SIGNING_KEY": SECRET_SIGNING_KEY,
}
