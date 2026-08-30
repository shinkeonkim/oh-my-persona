from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from stocks.models import DerivedIndicator
from unfold.admin import ModelAdmin


@admin.register(DerivedIndicator)
class DerivedIndicatorAdmin(ModelAdmin):
  """파생지표 어드민"""

  list_display = (
    "stock_code_display",
    "stock_name_display",
    "company_name_display",
    "period_display",
    "per_display",
    "pbr_display",
    "roe_display",
    "roa_display",
    "reference_date",
  )

  list_filter = (
    "fiscal_year",
    "fiscal_quarter",
    ("stock__market", admin.RelatedOnlyFieldListFilter),
  )

  search_fields = (
    "stock__code",
    "stock__name",
    "company__name",
  )

  readonly_fields = (
    "stock",
    "company",
    "financial_statement",
    "fiscal_year",
    "fiscal_quarter",
    "reference_price",
    "reference_date",
    "market_cap",
    "per",
    "eps",
    "pbr",
    "bps",
    "roe",
    "roa",
    "dividend_yield",
    "dps",
    "net_income",
    "total_equity",
    "total_assets",
    "total_shares",
    "calculation_notes",
    "created_at",
    "updated_at",
  )

  autocomplete_fields = ("stock", "company")
  list_filter_submit = True
  list_filter_sheet = False

  ordering = ("-fiscal_year", "-fiscal_quarter", "stock__code")

  fieldsets = (
    (
      "기본 정보",
      {
        "fields": (
          "stock",
          "company",
          "financial_statement",
          "fiscal_year",
          "fiscal_quarter",
        )
      },
    ),
    (
      "기준 정보",
      {
        "fields": (
          "reference_date",
          "reference_price",
          "market_cap",
          "total_shares",
        )
      },
    ),
    (
      "주가 배수 지표",
      {
        "fields": (
          ("per", "eps"),
          ("pbr", "bps"),
        )
      },
    ),
    (
      "수익성 지표",
      {
        "fields": (("roe", "roa"), )
      },
    ),
    (
      "배당 지표",
      {
        "fields": (("dividend_yield", "dps"), )
      },
    ),
    (
      "재무제표 주요 수치",
      {
        "fields": (
          "net_income",
          "total_equity",
          "total_assets",
        )
      },
    ),
    (
      "메타데이터",
      {
        "fields": (
          "calculation_notes",
          "created_at",
          "updated_at",
        ),
        "classes": ["collapse"],
      },
    ),
  )

  def stock_code_display(self, obj):
    """종목 코드 표시"""
    return obj.stock.code

  stock_code_display.short_description = _("종목코드")
  stock_code_display.admin_order_field = "stock__code"

  def stock_name_display(self, obj):
    """종목명 표시"""
    return obj.stock.name

  stock_name_display.short_description = _("종목명")
  stock_name_display.admin_order_field = "stock__name"

  def company_name_display(self, obj):
    """회사명 표시"""
    return obj.company.name

  company_name_display.short_description = _("회사명")
  company_name_display.admin_order_field = "company__name"

  def period_display(self, obj):
    """기간 표시"""
    return f"{obj.fiscal_year}Q{obj.fiscal_quarter}"

  period_display.short_description = _("기간")
  period_display.admin_order_field = "fiscal_year"

  @admin.display(description=_("PER"), ordering="per")
  def per_display(self, obj):
    """PER 표시"""
    if obj.per is None:
      return "-"
    return format_html('<span style="font-weight: 500;">{}</span>', f"{float(obj.per):.2f}")

  @admin.display(description=_("PBR"), ordering="pbr")
  def pbr_display(self, obj):
    """PBR 표시"""
    if obj.pbr is None:
      return "-"
    return format_html('<span style="font-weight: 500;">{}</span>', f"{float(obj.pbr):.2f}")

  @admin.display(description=_("ROE"), ordering="roe")
  def roe_display(self, obj):
    """ROE 표시"""
    if obj.roe is None:
      return "-"
    return format_html('<span style="font-weight: 500;">{}</span>', f"{float(obj.roe):.2f}%")

  @admin.display(description=_("ROA"), ordering="roa")
  def roa_display(self, obj):
    """ROA 표시"""
    if obj.roa is None:
      return "-"
    return format_html('<span style="font-weight: 500;">{}</span>', f"{float(obj.roa):.2f}%")

  def has_add_permission(self, request):
    """생성 권한 비활성화 (서비스를 통해서만 생성)"""
    return False
