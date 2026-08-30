"""
Financial Statement Item Mapping Rule Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from financial_statements.models import FinancialStatementItemMappingRule
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeNumericFilter


@admin.register(FinancialStatementItemMappingRule)
class FinancialStatementItemMappingRuleAdmin(ModelAdmin):
  """재무제표 항목 매핑 규칙 어드민"""

  list_display = (
    "id",
    "scope_badge",
    "source_display",
    "arrow",
    "target_display",
    "priority",
    "is_active",
    "created_at",
  )
  list_filter = (
    ["is_active", ChoicesDropdownFilter],
    ["priority", RangeNumericFilter],
    "company",
  )
  search_fields = (
    "company__name",
    "source_account_id",
    "source_account_name",
    "target_account_id",
    "target_account_name",
  )
  readonly_fields = (
    "created_at",
    "updated_at",
  )
  ordering = ("-priority", "company", "source_account_name")

  # Unfold filter settings
  list_filter_submit = True
  list_filter_sheet = False

  fieldsets = (
    (
      _("적용 범위"),
      {
        "fields": (
          "company",
          "priority",
          "is_active",
        )
      },
    ),
    (
      _("Source (변환 전)"),
      {
        "fields": (
          "source_account_id",
          "source_account_name",
        )
      },
    ),
    (
      _("Target (변환 후)"),
      {
        "fields": (
          "target_account_id",
          "target_account_name",
        )
      },
    ),
    (
      _("메모"),
      {
        "fields": ("description", ),
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

  def scope_badge(self, obj):
    """적용 범위 뱃지"""
    if obj.company:
      return format_html(
        '<span style="background-color: #1976d2; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
        obj.company.name[:10],
      )
    return format_html(
      '<span style="background-color: #f57c00; color: white; padding: 3px 8px;'
      'border-radius: 3px; font-weight: bold;">전체</span>',
    )

  scope_badge.short_description = _("적용 범위")
  scope_badge.admin_order_field = "company"

  def source_display(self, obj):
    """Source 표시"""
    return format_html(
      '<div style="padding: 5px; background-color: #ffebee; border-radius: 3px;">'
      '<div><strong>{}</strong></div>'
      '<small style="color: #999;">{}</small>'
      '</div>',
      obj.source_account_name,
      obj.source_account_id,
    )

  source_display.short_description = _("변환 전")
  source_display.admin_order_field = "source_account_name"

  def arrow(self, obj):
    """화살표"""
    return format_html('<span style="font-size: 18px; color: #4caf50;">→</span>')

  arrow.short_description = ""

  def target_display(self, obj):
    """Target 표시"""
    # IFRS 표준 코드면 녹색으로 강조
    if obj.target_account_id.startswith("ifrs_"):
      bg_color = "#e8f5e9"
      text_color = "#2e7d32"
      icon = "✓"
    else:
      bg_color = "#e3f2fd"
      text_color = "#1565c0"
      icon = ""

    return format_html(
      '<div style="padding: 5px; background-color: {}; border-radius: 3px;">'
      '<div><strong style="color: {};">{} {}</strong></div>'
      '<small style="color: {};">{}</small>'
      '</div>',
      bg_color,
      text_color,
      icon,
      obj.target_account_name,
      text_color,
      obj.target_account_id,
    )

  target_display.short_description = _("변환 후")
  target_display.admin_order_field = "target_account_name"

  def get_queryset(self, request):
    """쿼리셋 최적화"""
    queryset = super().get_queryset(request)
    return queryset.select_related("company")

  # Actions
  actions = ["activate_rules", "deactivate_rules"]

  @admin.action(description=_("선택한 규칙 활성화"))
  def activate_rules(self, request, queryset):
    """규칙 활성화"""
    updated = queryset.update(is_active=True)
    self.message_user(request, f"{updated}개 규칙을 활성화했습니다.")

  @admin.action(description=_("선택한 규칙 비활성화"))
  def deactivate_rules(self, request, queryset):
    """규칙 비활성화"""
    updated = queryset.update(is_active=False)
    self.message_user(request, f"{updated}개 규칙을 비활성화했습니다.")
