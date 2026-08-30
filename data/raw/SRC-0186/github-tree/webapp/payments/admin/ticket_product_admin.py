from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from payments.models import TicketProduct


@admin.register(TicketProduct)
class TicketProductAdmin(ModelAdmin):
  """티켓 상품 관리"""

  list_display = [
    "quantity",
    "price_display",
    "unit_price_display",
    "original_price_display",
    "discount_rate_display",
    "is_active",
    "display_order",
    "created_at",
  ]
  list_filter = ["is_active", "created_at"]
  search_fields = ["quantity"]
  list_editable = ["is_active", "display_order"]
  ordering = ["display_order", "quantity"]
  list_filter_submit = True
  list_filter_sheet = False

  fieldsets = (
    (
      "상품 정보",
      {
        "fields": (
          "quantity",
          "price",
          "discount_rate",
        )
      },
    ),
    (
      "판매 설정",
      {
        "fields": (
          "is_active",
          "display_order",
        )
      },
    ),
    (
      "타임스탬프",
      {
        "fields": (
          "created_at",
          "updated_at",
        ),
        "classes": ("collapse", ),
      },
    ),
  )

  readonly_fields = ["discount_rate", "created_at", "updated_at"]

  @admin.display(description="가격", ordering="price")
  def price_display(self, obj):
    """가격 포맷"""
    return format_html("<strong>{}원</strong>", f"{obj.price:,}")

  @admin.display(description="개당 단가")
  def unit_price_display(self, obj):
    """개당 단가 포맷"""
    return format_html("{}원", f"{obj.unit_price:,}")

  @admin.display(description="정가")
  def original_price_display(self, obj):
    """정가 포맷"""
    if obj.discount_rate > 0:
      return format_html(
        '<span style="text-decoration: line-through; color: gray;">{}원</span>',
        f"{obj.original_price:,}",
      )
    return format_html("{}원", f"{obj.original_price:,}")

  @admin.display(description="할인율")
  def discount_rate_display(self, obj):
    """할인율 포맷"""
    if obj.discount_rate > 0:
      return format_html(
        '<span style="color: red; font-weight: bold;">{}%</span>',
        f"{obj.discount_rate:.0f}",
      )
    return "-"

  def save_model(self, request, obj, form, change):
    """
        저장 시 자동으로 할인율 계산
        (모델의 save 메서드에서 처리되지만 명시적으로 표시)
        """
    super().save_model(request, obj, form, change)
