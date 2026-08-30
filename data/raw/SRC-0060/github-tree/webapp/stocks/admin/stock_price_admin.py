from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from stocks.models import StockPrice
from stocks.views import StockPriceIngestView
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  AutocompleteSelectFilter,
  RangeDateFilter,
)
from unfold.decorators import action


@admin.register(StockPrice)
class StockPriceAdmin(ModelAdmin):
  list_display = (
    "trade_date",
    "stock",
    "market",
    "close_price",
    "change_rate",
    "volume",
    "market_cap",
  )
  search_fields = ("stock__code", "stock__name")
  list_filter = (
    ("trade_date", RangeDateFilter),
    "market",
    "stock__category",
    ("stock", AutocompleteSelectFilter),
  )
  ordering = ("-trade_date", "stock__code")
  date_hierarchy = "trade_date"
  autocomplete_fields = (
    "stock",
    "market",
  )

  # Unfold filter settings
  list_filter_submit = True  # 필터 제출 버튼 추가
  list_filter_sheet = False  # 사이드바 필터 대신 상단 필터 사용

  # Unfold changelist actions
  actions_list = ["ingest_stock_prices"]

  @action(
    description=_("Ingest stock prices"),
    permissions=["ingest_stock_prices"],
    url_path="ingest-stock-prices",
  )
  def ingest_stock_prices(self, request):
    """주식 가격 수집 페이지로 리다이렉트"""
    return HttpResponseRedirect(reverse("admin:companies_stockprice_ingest"))

  def has_ingest_stock_prices_permission(self, request):
    """주식 가격 수집 액션 권한 체크"""
    return request.user.has_perm("companies.view_stockprice")

  def get_urls(self):
    """커스텀 URL 추가"""
    urls = super().get_urls()
    custom_urls = [
      path(
        "ingest/",
        self.admin_site.admin_view(StockPriceIngestView.as_view(model_admin=self)),
        name="companies_stockprice_ingest",
      ),
    ]
    return custom_urls + urls
