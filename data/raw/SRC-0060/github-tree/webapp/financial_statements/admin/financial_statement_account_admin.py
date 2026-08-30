"""
Financial Statement Account Admin (Clean)
"""
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from financial_statements.models import FinancialStatementAccount
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter


@admin.register(FinancialStatementAccount)
class FinancialStatementAccountAdmin(ModelAdmin):
  """정제된 재무제표 계정과목 어드민"""

  list_display = (
    "id",
    "account_name_display",
    "account_id_display",
    "account_category_badge",
    "category_name",
    "usage_count",
    "created_at",
  )
  list_filter = (
    ["account_category", ChoicesDropdownFilter],
    "category_name",
  )
  search_fields = (
    "account_id",
    "account_name",
    "category_name",
  )
  readonly_fields = (
    "created_at",
    "updated_at",
    "usage_count",
  )
  ordering = ("account_category", "account_name")

  # Unfold filter settings
  list_filter_submit = True
  list_filter_sheet = False

  fieldsets = (
    (
      _("계정과목 정보"),
      {
        "fields": (
          "account_id",
          "account_name",
        )
      },
    ),
    (
      _("분류 정보"),
      {
        "fields": (
          "account_category",
          "category_name",
          "account_detail",
        )
      },
    ),
    (
      _("통계"),
      {
        "fields": ("usage_count", ),
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
    return queryset.annotate(items_count=Count("items"))

  def account_name_display(self, obj):
    """계정과목명 표시"""
    return format_html(
      '<strong style="color: #2e7d32;">{}</strong>',
      obj.account_name,
    )

  account_name_display.short_description = _("계정과목명")
  account_name_display.admin_order_field = "account_name"

  def account_id_display(self, obj):
    """계정과목 ID 표시"""
    if obj.account_id == "-표준계정코드 미사용-":
      return format_html(
        '<span style="color: #999; font-style: italic;">{}</span>',
        obj.account_id,
      )
    # IFRS 표준 코드는 녹색으로 표시
    if obj.account_id.startswith("ifrs_"):
      return format_html(
        '<span style="color: #2e7d32; font-weight: 500;">{}</span>',
        obj.account_id,
      )
    return obj.account_id

  account_id_display.short_description = _("계정과목 ID")
  account_id_display.admin_order_field = "account_id"

  def account_category_badge(self, obj):
    """계정과목 분류 뱃지"""
    colors = {
      "BS": "primary",
      "IS": "success",
      "CIS": "success",
      "CF": "warning",
      "SCE": "info",
    }
    color = colors.get(obj.account_category, "secondary")
    return format_html(
      '<span style="background-color: {}; color: white; padding: 3px 8px;'
      'border-radius: 3px; font-weight: bold;">{}</span>',
      color,
      obj.account_category or "-",
    )

  account_category_badge.short_description = _("분류")
  account_category_badge.admin_order_field = "account_category"

  def usage_count(self, obj):
    """사용 횟수"""
    if hasattr(obj, "items_count"):
      return obj.items_count
    return obj.items.count()

  usage_count.short_description = _("사용 횟수")
  usage_count.admin_order_field = "items_count"
