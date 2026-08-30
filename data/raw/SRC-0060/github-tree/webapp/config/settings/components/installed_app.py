# Application definition

ADMIN_APPS = [
  "unfold",
  "unfold.contrib.filters",
  "unfold.contrib.forms",
  "unfold.contrib.inlines",
  "unfold.contrib.import_export",
  "admin_object_actions",
]

DJANGO_APPS = [
  "corsheaders",
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
]

PACKAGE_APPS = [
  # Django Postgres
  "django.contrib.postgres",
  "psqlextra",
  # Django Extensions
  "django_extensions",
  # NPlusOne
  "nplusone.ext.django",
  # REST Framework
  "rest_framework",
  "rest_framework.authtoken",
  "rest_framework_simplejwt",
  "rest_framework_simplejwt.token_blacklist",
  # Swagger Docs
  "drf_spectacular",
  # Django Filters
  "django_filters",
  # Logging
  "django_guid",
  # Django ADMIN Import Export
  "import_export",
  # Auth
  "allauth",
  "allauth.account",
  "dj_rest_auth",
  "dj_rest_auth.registration",
  "allauth.socialaccount",
  "allauth.socialaccount.providers.kakao",
  "allauth.socialaccount.providers.google",
  # Celery
  "django_celery_beat",
  "django_celery_results",
]

CUSTOM_APPS = [
  "common",
  "api",
  "users",
  "companies",
  "stocks",
  "disclosures",
  "financial_statements",
  "watchlists",
]

INSTALLED_APPS = ADMIN_APPS + DJANGO_APPS + PACKAGE_APPS + CUSTOM_APPS

__all__ = [
  "INSTALLED_APPS",
]
