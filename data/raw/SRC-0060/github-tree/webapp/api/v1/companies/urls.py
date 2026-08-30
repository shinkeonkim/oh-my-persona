from django.urls import path

from .views import (
  CompanyDetailAPIView,
  CompanyListAPIView,
)

urlpatterns = [
  # Company endpoints
  path("companies/", CompanyListAPIView.as_view(), name="company-list"),
  path("companies/<str:corp_code>/", CompanyDetailAPIView.as_view(), name="company-detail"),
]
