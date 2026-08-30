"""
URL configuration for palette_api project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularRedocView,
  SpectacularSwaggerView,
)

urlpatterns = [
  path("admin/", include("users.admin.urls")),
  path("admin/", admin.site.urls),
  path("api/", include("api.urls")),
  path("health/", include("api.v1.health_check.urls")),
]

if settings.ENVIRONMENT != "production":
  urlpatterns += [
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
  ]

if settings.ENVIRONMENT == "production":
  urlpatterns += [
    path("", include("api.v1.health_check.urls")),
  ]

if settings.DEBUG:
  urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
  ]
