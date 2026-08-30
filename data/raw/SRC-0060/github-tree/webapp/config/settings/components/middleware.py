MIDDLEWARE = [
  "allow_cidr.middleware.AllowCIDRMiddleware",
  "corsheaders.middleware.CorsMiddleware",
  "django_guid.middleware.guid_middleware",
  "crum.CurrentRequestUserMiddleware",
  "nplusone.ext.django.NPlusOneMiddleware",
  "allauth.account.middleware.AccountMiddleware",
  "django.middleware.security.SecurityMiddleware",
  "django.contrib.sessions.middleware.SessionMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.contrib.auth.middleware.AuthenticationMiddleware",
  "django.contrib.messages.middleware.MessageMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware",
  "common.middlewares.CamelCaseMiddleware",
]

__all__ = [
  "MIDDLEWARE",
]
