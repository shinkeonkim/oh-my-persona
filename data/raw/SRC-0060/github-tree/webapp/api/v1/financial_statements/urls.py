from django.urls import path

from .views import CompanyFinancialStatementDetailAPIView, CompanyFinancialStatementListAPIView

urlpatterns = [
  path(
    "companies/<str:corp_code>/financial-statements/",
    CompanyFinancialStatementListAPIView.as_view(),
    name="company-financial-statements-list",
  ),
  path(
    "companies/<str:corp_code>/financial-statements/<int:pk>/",
    CompanyFinancialStatementDetailAPIView.as_view(),
    name="company-financial-statements-detail",
  ),
]
