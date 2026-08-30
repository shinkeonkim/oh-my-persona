from django.urls import path

from .views import CompanyDisclosureDetailAPIView, CompanyDisclosureListAPIView

urlpatterns = [
  path("company-disclosures/", CompanyDisclosureListAPIView.as_view(), name="company-disclosure-list"),
  path("company-disclosures/<int:pk>/", CompanyDisclosureDetailAPIView.as_view(), name="company-disclosure-detail"),
]
