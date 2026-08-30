"""
Financial Statement Admin
"""
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from financial_statements.models import FinancialStatement, FinancialStatementItem, RawFinancialStatementItem
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
  ChoicesDropdownFilter,
  RangeDateFilter,
  RangeNumericFilter,
)


class RawFinancialStatementItemInline(TabularInline):
  """원본 재무제표 항목 인라인 (Raw Data)"""

  model = RawFinancialStatementItem
  extra = 0
  fields = (
    "account",
    "current_amount",
    "cumulative_amount",
    "order",
  )
  readonly_fields = (
    "account",
    "current_amount",
    "cumulative_amount",
    "order",
  )
  ordering = ["order"]
  can_delete = False
  verbose_name = _("원본 재무제표 항목 (Raw)")
  verbose_name_plural = _("원본 재무제표 항목 (Raw)")

  def get_queryset(self, request):
    """N+1 쿼리 방지: account를 미리 로드"""
    return super().get_queryset(request).select_related("account")

  def has_add_permission(self, request, obj=None):
    return False


class FinancialStatementItemInline(TabularInline):
  """정제된 재무제표 항목 인라인 (Clean Data)"""

  model = FinancialStatementItem
  extra = 0
  fields = (
    "account_display",
    "current_amount",
    "cumulative_amount",
    "order",
  )
  readonly_fields = (
    "account_display",
    "current_amount",
    "cumulative_amount",
    "order",
  )
  ordering = ["order"]
  can_delete = False
  verbose_name = _("정제된 재무제표 항목 (Clean)")
  verbose_name_plural = _("정제된 재무제표 항목 (Clean)")

  def get_queryset(self, request):
    """N+1 쿼리 방지: account를 미리 로드"""
    return super().get_queryset(request).select_related("account")

  def has_add_permission(self, request, obj=None):
    return False

  def account_display(self, obj):
    """계정 표시 (IFRS 코드 강조)"""
    if obj.account.account_id.startswith("ifrs_"):
      return format_html(
        '<div><strong style="color: #2e7d32;">✓ {}</strong><br/>'
        '<span style="color: #666; font-size: 0.9em;">{}</span></div>',
        obj.account.account_name,
        obj.account.account_id,
      )
    return format_html(
      '<div><strong>{}</strong><br/><span style="color: #666; font-size: 0.9em;">{}</span></div>',
      obj.account.account_name,
      obj.account.account_id,
    )

  account_display.short_description = _("계정")


@admin.register(FinancialStatement)
class FinancialStatementAdmin(ModelAdmin):
  """재무제표 어드민"""

  list_display = (
    "id",
    "company_link",
    "fiscal_year",
    "fiscal_quarter",
    "report_type_badge",
    "source_badge",
    "is_consolidated",
    "currency",
    "submission_date",
  )
  list_filter = (
    ["source", ChoicesDropdownFilter],
    ["report_type", ChoicesDropdownFilter],
    ["is_consolidated", ChoicesDropdownFilter],
    "currency",
    ["fiscal_year", RangeNumericFilter],
    ["fiscal_quarter", ChoicesDropdownFilter],
    ["submission_date", RangeDateFilter],
  )
  search_fields = (
    "company__name",
    "company__corp_code",
    "receipt_no",
  )
  readonly_fields = (
    "created_at",
    "updated_at",
  )
  ordering = ("-fiscal_year", "-fiscal_quarter", "company__name", "source")

  # Unfold filter settings
  list_filter_submit = True
  list_filter_sheet = False

  # Inlines - Raw와 Clean 데이터 모두 표시
  inlines = [RawFinancialStatementItemInline, FinancialStatementItemInline]

  # Actions
  actions = ["preview_with_parser"]

  fieldsets = (
    (
      _("기본 정보"),
      {
        "fields": (
          "company",
          "fiscal_year",
          "fiscal_quarter",
          "report_type",
          "source",
          "is_consolidated",
        )
      },
    ),
    (
      _("제출 정보"),
      {
        "fields": (
          "receipt_no",
          "submission_date",
          "currency",
        )
      },
    ),
    (
      _("메타데이터"),
      {
        "fields": (
          "created_at",
          "updated_at",
        ),
        "classes": ["collapse"],
      },
    ),
  )

  def get_queryset(self, request):
    """쿼리셋 최적화"""
    queryset = super().get_queryset(request)
    return queryset.select_related("company")

  def company_link(self, obj):
    """회사 링크"""
    return format_html(
      '<a href="/admin/companies/company/{}/change/">{}</a>',
      obj.company.id,
      obj.company.name,
    )

  company_link.short_description = _("회사")
  company_link.admin_order_field = "company__name"

  def report_type_badge(self, obj):
    """보고서 유형 뱃지"""
    colors = {
      "q1": "info",
      "half": "warning",
      "q3": "info",
      "annual": "success",
    }
    color = colors.get(obj.report_type, "secondary")
    return format_html(
      '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
      color,
      obj.get_report_type_display(),
    )

  report_type_badge.short_description = _("보고서 유형")
  report_type_badge.admin_order_field = "report_type"

  def source_badge(self, obj):
    """재무제표 구분 뱃지"""
    colors = {
      "CFS": "primary",
      "OFS": "secondary",
    }
    color = colors.get(obj.source, "secondary")
    return format_html(
      '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
      color,
      obj.get_source_display(),
    )

  source_badge.short_description = _("재무제표 구분")
  source_badge.admin_order_field = "source"

  def preview_with_parser(self, request, queryset):
    """파서 미리보기 페이지로 리다이렉트"""
    selected = queryset.first()
    if selected:
      url = reverse("admin:financial_statements_financialstatement_parser_preview")
      return HttpResponseRedirect(f"{url}?statement_id={selected.id}")
    return HttpResponseRedirect(request.get_full_path())

  preview_with_parser.short_description = _("Preview with Parser")
  preview_with_parser.allowed_permissions = ("view", )

  def get_urls(self):
    """커스텀 URL 추가"""
    from django.urls import path
    urls = super().get_urls()
    custom_urls = [
      path(
        "parser-preview/",
        self.admin_site.admin_view(self._parser_preview_view),
        name="financial_statements_financialstatement_parser_preview",
      ),
    ]
    return custom_urls + urls

  def _parser_preview_view(self, request):
    """파서 미리보기 뷰"""
    from financial_statements.views import ParserPreviewView
    return ParserPreviewView.as_view(model_admin=self)(request)
