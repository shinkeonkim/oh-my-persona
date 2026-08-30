from django.urls import path

from api.v1.stocks.views import (
  DerivedIndicatorDetailAPIView,
  DerivedIndicatorListAPIView,
  StockDetailAPIView,
  StockListAPIView,
  StockPriceListAPIView,
)

urlpatterns = [
  path("stocks/", StockListAPIView.as_view(), name="stock-list"),
  path("stocks/<str:code>/", StockDetailAPIView.as_view(), name="stock-detail"),
  path("stocks/<str:code>/prices/", StockPriceListAPIView.as_view(), name="stock-price-list"),
  path(
    "stocks/<str:code>/derived-indicators/",
    DerivedIndicatorListAPIView.as_view(),
    name="derived-indicator-list",
  ),
  path(
    "stocks/<str:code>/derived-indicators/<int:id>/",
    DerivedIndicatorDetailAPIView.as_view(),
    name="derived-indicator-detail",
  ),
]
