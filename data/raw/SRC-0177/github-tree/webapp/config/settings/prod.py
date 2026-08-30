from .base import *  # noqa: F401, F403

ALLOWED_HOSTS = ["api.memez.party", "memez.party"]
CSRF_TRUSTED_ORIGINS = ["https://api.memez.party", "https://memez.party"]

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": "postgres",
        "PORT": env("POSTGRES_PORT"),
    }
}

# Static files (CSS, JavaScript, Images)

STATIC_DIR = f"{BASE_DIR}/static"
STATIC_ROOT = f"{BASE_DIR}/static"
STATIC_URL = "/static/"

# Media files
MEDIA_ROOT = f"{BASE_DIR}/media"
MEDIA_URL = "media/"

BASE_URL = "https://api.memez.party/"
KAKAO_CALLBACK_URI = BASE_URL + "api/v1/accounts/kakao/login/callback/"
# ========== Logging settings ==========

LOGGING = get_logging_config(BASE_DIR, debug=DEBUG, environment="prod")

# ========== END Logging settings ==========
