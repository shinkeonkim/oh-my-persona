import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from stocks.models import Stock, StockPrice
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectMultipleFilter
from unfold.decorators import action
from unfold.sections import TemplateSection

from companies.models import Company
from companies.views import (
  BulkFinancialStatementIngestAndRegenerationView,
  DartCompanyIngestView,
  DisclosureIngestView,
  FinancialStatementIngestAndRegenerationView,
  FinancialStatementIngestView,
  FinancialStatementRegenerationView,
)

logger = logging.getLogger(__name__)

DISCLOSURE_WINDOW_DAYS = getattr(settings, "DISCLOSURE_DEFAULT_WINDOW_DAYS", 30)


class StockInline(TabularInline):
  """회사의 주식 목록 인라인"""
  model = Stock
  extra = 0
  fields = ("code", "name", "market", "category", "is_primary", "is_listed", "currency")
  readonly_fields = ("code", "name", "market", "category", "is_primary", "is_listed", "currency")
  can_delete = False

  def has_add_permission(self, request, obj=None):
    return False


class StockInfoSection(TemplateSection):
  """회사의 주식 목록 및 최근 10일 주가 차트 섹션"""

  title = _("주식 정보 및 주가 차트")
  template_name = "admin/companies/company/stock_info_section.html"


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
  list_display = (
    "name",
    "corp_code",
    "country",
    "sector",
    "industry",
    "is_fixed_sector",
    "is_fixed_industry",
    "is_financial",
  )
  search_fields = ("name", "corp_code", "sector__name", "industry__name")
  list_filter = (
    ["country", AutocompleteSelectMultipleFilter],
    ["sector", AutocompleteSelectMultipleFilter],
    ["industry", AutocompleteSelectMultipleFilter],
    "is_fixed_sector",
    "is_fixed_industry",
    "is_financial",
  )
  autocomplete_fields = ()
  inlines = [StockInline]
  list_filter_submit = True
  list_filter_sheet = False

  # Unfold sections - 펼칠 수 있는 섹션
  list_sections = [StockInfoSection]

  # Django admin actions (선택한 항목에 대한 액션)
  actions = [
    "queue_disclosure_ingest",
    "queue_financial_statement_ingest",
    "queue_financial_statement_regeneration",
    "queue_financial_statement_ingest_and_regeneration",
  ]

  # Unfold changelist actions
  actions_list = ["queue_dart_company_ingest", "queue_bulk_financial_statement_ingest_and_regeneration"]

  def get_queryset(self, request):
    """쿼리셋 최적화: 섹션에서 사용할 관련 데이터 prefetch"""
    queryset = super().get_queryset(request)

    # 최근 10일 날짜 계산
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=10)

    # 주식과 최근 10일 주가 데이터를 prefetch
    recent_prices_prefetch = Prefetch(
      'stocks__prices',
      queryset=StockPrice.objects.filter(trade_date__gte=start_date, trade_date__lte=end_date).order_by('trade_date'),
      to_attr='recent_prices'
    )

    return queryset.prefetch_related('stocks', 'stocks__market',
                                     recent_prices_prefetch).select_related('country', 'sector', 'industry')

  @action(
    description=_("Fetch DART company data"),
    permissions=["queue_dart_company_ingest"],
    url_path="queue-dart-company-ingest",
  )
  def queue_dart_company_ingest(self, request):
    """DART 회사 정보 수집 페이지로 리다이렉트"""
    from django.urls import reverse
    return HttpResponseRedirect(reverse("admin:companies_dart_company_ingest"))

  def has_queue_dart_company_ingest_permission(self, request):
    """Queue DART company ingest 액션 권한 체크"""
    return request.user.has_perm("companies.change_company")

  @action(
    description=_("Bulk collect financial statements for all companies"),
    permissions=["queue_bulk_financial_statement_ingest_and_regeneration"],
    url_path="queue-bulk-financial-statement-ingest-and-regeneration",
  )
  def queue_bulk_financial_statement_ingest_and_regeneration(self, request):
    """전체 회사 재무제표 배치 수집 페이지로 리다이렉트"""
    from django.urls import reverse
    return HttpResponseRedirect(reverse("admin:companies_bulk_financial_statement_ingest_and_regeneration"))

  def has_queue_bulk_financial_statement_ingest_and_regeneration_permission(self, request):
    """Queue bulk financial statement ingest and regeneration 액션 권한 체크"""
    return request.user.has_perm("companies.change_company")

  def queue_disclosure_ingest(self, request, queryset):
    """공시 정보 수집 페이지로 리다이렉트"""
    from django.urls import reverse

    # queryset에서 선택된 회사들의 ID 가져오기
    selected_ids = list(queryset.values_list('pk', flat=True))

    if not selected_ids:
      self.message_user(
        request,
        _("Select at least one company to queue disclosure ingestion."),
        level=messages.WARNING,
      )
      return HttpResponseRedirect(request.get_full_path())

    # 선택된 ID를 쉼표로 구분하여 단일 파라미터로 전달
    url = reverse("admin:companies_company_disclosure_ingest")
    ids_param = ",".join(str(id) for id in selected_ids)
    return HttpResponseRedirect(f"{url}?ids={ids_param}")

  queue_disclosure_ingest.short_description = _("Queue DART disclosure ingestion")
  queue_disclosure_ingest.allowed_permissions = ('change', )

  def queue_financial_statement_ingest(self, request, queryset):
    """재무제표 정보 수집 페이지로 리다이렉트"""
    from django.urls import reverse

    # queryset에서 선택된 회사들의 ID 가져오기
    selected_ids = list(queryset.values_list('pk', flat=True))

    if not selected_ids:
      self.message_user(
        request,
        _("Select at least one company to queue financial statement ingestion."),
        level=messages.WARNING,
      )
      return HttpResponseRedirect(request.get_full_path())

    # 선택된 ID를 쉼표로 구분하여 단일 파라미터로 전달
    url = reverse("admin:companies_company_financial_statement_ingest")
    ids_param = ",".join(str(id) for id in selected_ids)
    return HttpResponseRedirect(f"{url}?ids={ids_param}")

  queue_financial_statement_ingest.short_description = _("Queue financial statement ingestion (Raw)")

  def queue_financial_statement_regeneration(self, request, queryset):
    """재무제표 재생성 페이지로 리다이렉트"""
    from django.urls import reverse

    # queryset에서 선택된 회사들의 ID 가져오기
    selected_ids = list(queryset.values_list('pk', flat=True))

    if not selected_ids:
      self.message_user(
        request,
        _("Select at least one company to regenerate financial statements."),
        level=messages.WARNING,
      )
      return HttpResponseRedirect(request.get_full_path())

    # 선택된 ID를 쉼표로 구분하여 단일 파라미터로 전달
    url = reverse("admin:companies_company_financial_statement_regeneration")
    ids_param = ",".join(str(id) for id in selected_ids)
    return HttpResponseRedirect(f"{url}?ids={ids_param}")

  queue_financial_statement_regeneration.short_description = _("Regenerate financial statements (Clean)")

  def queue_financial_statement_ingest_and_regeneration(self, request, queryset):
    """재무제표 수집 및 재생성 통합 페이지로 리다이렉트"""
    from django.urls import reverse

    # queryset에서 선택된 회사들의 ID 가져오기
    selected_ids = list(queryset.values_list('pk', flat=True))

    if not selected_ids:
      self.message_user(
        request,
        _("Select at least one company to queue financial statement ingest and regeneration."),
        level=messages.WARNING,
      )
      return HttpResponseRedirect(request.get_full_path())

    # 선택된 ID를 쉼표로 구분하여 단일 파라미터로 전달
    url = reverse("admin:companies_company_financial_statement_ingest_and_regeneration")
    ids_param = ",".join(str(id) for id in selected_ids)
    return HttpResponseRedirect(f"{url}?ids={ids_param}")

  queue_financial_statement_ingest_and_regeneration.short_description = _(
    "Ingest and regenerate financial statements (Complete)"
  )

  def get_urls(self):
    """커스텀 URL 추가"""
    from django.urls import path
    urls = super().get_urls()
    custom_urls = [
      path(
        "dart-company-ingest/",
        self.admin_site.admin_view(DartCompanyIngestView.as_view(model_admin=self)),
        name="companies_dart_company_ingest",
      ),
      path(
        "disclosure-ingest/",
        self.admin_site.admin_view(DisclosureIngestView.as_view(model_admin=self)),
        name="companies_company_disclosure_ingest",
      ),
      path(
        "financial-statement-ingest/",
        self.admin_site.admin_view(FinancialStatementIngestView.as_view(model_admin=self)),
        name="companies_company_financial_statement_ingest",
      ),
      path(
        "financial-statement-regeneration/",
        self.admin_site.admin_view(FinancialStatementRegenerationView.as_view(model_admin=self)),
        name="companies_company_financial_statement_regeneration",
      ),
      path(
        "financial-statement-ingest-and-regeneration/",
        self.admin_site.admin_view(FinancialStatementIngestAndRegenerationView.as_view(model_admin=self)),
        name="companies_company_financial_statement_ingest_and_regeneration",
      ),
      path(
        "bulk-financial-statement-ingest-and-regeneration/",
        self.admin_site.admin_view(BulkFinancialStatementIngestAndRegenerationView.as_view(model_admin=self)),
        name="companies_bulk_financial_statement_ingest_and_regeneration",
      ),
    ]
    return custom_urls + urls
