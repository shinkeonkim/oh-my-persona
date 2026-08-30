from datetime import timedelta

from django.contrib import admin, messages
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from stocks.models import Stock, StockPrice
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.sections import TemplateSection


class StockPriceChartSection(TemplateSection):
  """주식 가격 차트 섹션"""

  title = _("주가 차트")
  template_name = "admin/companies/stock/price_chart_section.html"


@admin.register(Stock)
class StockAdmin(ModelAdmin):
  list_display = (
    "code",
    "name",
    "company",
    "market",
    "category",
    "is_primary",
    "is_listed",
    "currency",
  )
  search_fields = (
    "code",
    "name",
    "company__name",
  )
  list_filter = (
    "market",
    "category",
    "is_primary",
    "is_listed",
    "currency",
  )
  ordering = ("code", )
  autocomplete_fields = ("company", "market")
  list_filter_submit = True
  list_filter_sheet = False

  # Unfold sections - 주가 차트 섹션 추가
  list_sections = [StockPriceChartSection]

  # Django admin actions (선택한 항목에 대한 액션)
  actions = [
    "queue_derived_indicator_calculate",
  ]

  # Unfold changelist actions
  actions_list = ["queue_krx_stock_ingest", "queue_bulk_derived_indicator_calculate"]

  fieldsets = (
    ("기본 정보", {
      "fields": ("code", "name", "company", "market")
    }),
    ("주식 분류", {
      "fields": ("category", "is_primary")
    }),
    ("상장 정보", {
      "fields": ("is_listed", "listed_date", "delisted_date")
    }),
    ("거래 정보", {
      "fields": ("currency", "lot_size")
    }),
  )

  def get_queryset(self, request):
    """쿼리셋 최적화: 주가 데이터 prefetch"""
    queryset = super().get_queryset(request)

    # 최근 90일 날짜 계산
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)

    # 최근 90일 주가 데이터를 prefetch
    recent_prices_prefetch = Prefetch(
      'prices',
      queryset=StockPrice.objects.filter(trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date'),
      to_attr='recent_prices'
    )

    return queryset.prefetch_related(recent_prices_prefetch).select_related('company', 'market')

  @action(
    description=_("Fetch KRX stock data"),
    permissions=["queue_krx_stock_ingest"],
    url_path="queue-krx-stock-ingest",
  )
  def queue_krx_stock_ingest(self, request):
    """KRX 주식 정보 수집 페이지로 리다이렉트"""
    from django.urls import reverse
    return HttpResponseRedirect(reverse("admin:stocks_krx_stock_ingest"))

  def has_queue_krx_stock_ingest_permission(self, request):
    """Queue KRX stock ingest 액션 권한 체크"""
    return request.user.has_perm("stocks.change_stock")

  @action(
    description=_("Calculate derived indicators for all stocks"),
    permissions=["queue_bulk_derived_indicator_calculate"],
    url_path="queue-bulk-derived-indicator-calculate",
  )
  def queue_bulk_derived_indicator_calculate(self, request):
    """전체 종목 파생지표 계산 페이지로 리다이렉트"""
    from django.urls import reverse
    return HttpResponseRedirect(reverse("admin:stocks_bulk_derived_indicator_calculate"))

  def has_queue_bulk_derived_indicator_calculate_permission(self, request):
    """Queue bulk derived indicator calculate 액션 권한 체크"""
    return request.user.has_perm("stocks.change_stock")

  def queue_derived_indicator_calculate(self, request, queryset):
    """파생지표 계산 페이지로 리다이렉트"""
    from django.urls import reverse

    selected_ids = list(queryset.values_list('pk', flat=True))

    if not selected_ids:
      self.message_user(
        request,
        _("Select at least one stock to calculate derived indicators."),
        level=messages.WARNING,
      )
      return HttpResponseRedirect(request.get_full_path())

    url = reverse("admin:stocks_stock_derived_indicator_calculate")
    ids_param = ",".join(str(id) for id in selected_ids)
    return HttpResponseRedirect(f"{url}?ids={ids_param}")

  queue_derived_indicator_calculate.short_description = _("Calculate derived indicators (PER, PBR, ROE, ROA)")
  queue_derived_indicator_calculate.allowed_permissions = ('change', )

  def get_urls(self):
    """커스텀 URL 추가"""
    from django.urls import path

    from stocks.views import (
      BulkDerivedIndicatorCalculateView,
      DerivedIndicatorCalculateView,
      KrxStockIngestView,
    )

    urls = super().get_urls()
    custom_urls = [
      path(
        "krx-stock-ingest/",
        self.admin_site.admin_view(KrxStockIngestView.as_view(model_admin=self)),
        name="stocks_krx_stock_ingest",
      ),
      path(
        "derived-indicator-calculate/",
        self.admin_site.admin_view(DerivedIndicatorCalculateView.as_view(model_admin=self)),
        name="stocks_stock_derived_indicator_calculate",
      ),
      path(
        "bulk-derived-indicator-calculate/",
        self.admin_site.admin_view(BulkDerivedIndicatorCalculateView.as_view(model_admin=self)),
        name="stocks_bulk_derived_indicator_calculate",
      ),
    ]
    return custom_urls + urls
