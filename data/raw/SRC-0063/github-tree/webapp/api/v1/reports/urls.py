from django.urls import path

from .views import (
    ReportDetailAPIView,
    ReportEmailAPIView,
    ReportStatusAPIView,
    set_report_pin_api_view,
)

urlpatterns = [
    path("", ReportDetailAPIView.as_view(), name="report-detail"),
    path("status/", ReportStatusAPIView.as_view(), name="report-status"),
    path("email/", ReportEmailAPIView.as_view(), name="report-email"),
    path("set-report-pin/", set_report_pin_api_view.SetReportPinAPIView.as_view(), name="set-report-pin"),
]
