"""
Financial Statement Item Admin (Clean)
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from financial_statements.models import FinancialStatementItem
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter


@admin.register(FinancialStatementItem)
class FinancialStatementItemAdmin(ModelAdmin):
  """정제된 재무제표 항목 어드민"""

  list_display = (
    "id",
    "statement_link",
    "account_name_display",
    "current_amount_display",
    "cumulative_amount_display",
    "order",
    "created_at",
  )
  list_filter = (
    "statement__fiscal_year",
    ["statement__fiscal_quarter", ChoicesDropdownFilter],
    ["statement__source", ChoicesDropdownFilter],
    ["account__account_category", ChoicesDropdownFilter],
  )
  search_fields = (
    "statement__company__name",
    "account__account_name",
    "account__account_id",
  )
  readonly_fields = (
    "statement",
    "account",
    "current_amount",
    "cumulative_amount",
    "order",
    "raw",
    "created_at",
    "updated_at",
  )
  ordering = ("statement", "order")

  # Unfold filter settings
  list_filter_submit = True
  list_filter_sheet = False

  fieldsets = (
    (
      _("기본 정보"),
      {
        "fields": (
          "statement",
          "account",
        )
      },
    ),
    (
      _("금액 데이터"),
      {
        "fields": (
          "current_amount",
          "cumulative_amount",
        )
      },
    ),
    (
      _("메타데이터"),
      {
        "fields": (
          "order",
          "raw",
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
    return queryset.select_related("statement__company", "account")

  def has_add_permission(self, request):
    """추가 권한 없음 (재생성을 통해서만 생성)"""
    return False

  def has_delete_permission(self, request, obj=None):
    """삭제 권한 없음"""
    return False

  def statement_link(self, obj):
    """재무제표 링크"""
    return format_html(
      '<a href="/admin/financial_statements/financialstatement/{}/change/">{} {} Q{}</a>',
      obj.statement.id,
      obj.statement.company.name,
      obj.statement.fiscal_year,
      obj.statement.fiscal_quarter,
    )

  statement_link.short_description = _("재무제표")
  statement_link.admin_order_field = "statement__company__name"

  def account_name_display(self, obj):
    """계정과목명 표시 (정제된 데이터 강조)"""
    # IFRS 표준 코드면 녹색으로 강조
    if obj.account.account_id.startswith("ifrs_"):
      return format_html(
        '<div><strong style="color: #2e7d32;">✓ {}</strong><br><small style="color: #2e7d32;">{}</small></div>',
        obj.account.account_name,
        obj.account.account_id,
      )
    return format_html(
      '<div><strong>{}</strong><br><small style="color: #999;">{}</small></div>',
      obj.account.account_name,
      obj.account.account_id,
    )

  account_name_display.short_description = _("계정과목 (정제)")
  account_name_display.admin_order_field = "account__account_name"

  def current_amount_display(self, obj):
    """당기금액 표시"""
    if obj.current_amount is None:
      return "-"
    # Decimal을 먼저 float로 변환
    amount = float(obj.current_amount)
    formatted = f"{amount:,.0f}"
    return format_html(
      '<span style="text-align: right; display: block; font-weight: 500;">{}</span>',
      formatted,
    )

  current_amount_display.short_description = _("당기금액")
  current_amount_display.admin_order_field = "current_amount"

  def cumulative_amount_display(self, obj):
    """당기누적금액 표시"""
    if obj.cumulative_amount is None:
      return "-"
    # Decimal을 먼저 float로 변환
    amount = float(obj.cumulative_amount)
    formatted = f"{amount:,.0f}"
    return format_html(
      '<span style="text-align: right; display: block; font-weight: 500;">{}</span>',
      formatted,
    )

  cumulative_amount_display.short_description = _("당기누적금액")
  cumulative_amount_display.admin_order_field = "cumulative_amount"
