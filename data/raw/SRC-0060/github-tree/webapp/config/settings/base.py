"""
Django settings for webapp project.

- https://docs.djangoproject.com/en/5.2/topics/settings/
- https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from .components.admin import *
from .components.auth import *
from .components.celery import *
from .components.celery_beat import *
from .components.common import *
from .components.database import *
from .components.i18n import *
from .components.installed_app import *
from .components.middleware import *
from .components.rest_framework import *
from .components.slack import *
from .components.template import *

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

ROOT_URLCONF = "config.urls"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DART_API_KEY = env.str("DART_API_KEY", default="")

# KRX API Settings
KRX_OTP_URL = "https://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
KRX_COMPANY_INGEST_DOWNLOAD_URL = "https://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
KRX_STOCK_PRICE_DOWNLOAD_URL = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
KRX_REFERER = "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101"
KRX_ORIGIN = "https://data.krx.co.kr"
KRX_DEFAULT_MARKETS = ["STK", "KSQ"]
KRX_SLEEP = 1

DART_CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"
