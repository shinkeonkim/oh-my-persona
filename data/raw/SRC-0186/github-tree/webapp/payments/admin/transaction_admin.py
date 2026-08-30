from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from payments.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
  """거래 내역 관리"""

  list_display = [
    "id",
    "payment_order_id",
    "transaction_type_display",
    "amount_display",
    "success_display",
    "created_at",
  ]
  list_filter = ["transaction_type", "success", "created_at"]
  search_fields = [
    "payment__order_id",
    "transaction_key",
    "reason",
  ]
  readonly_fields = [
    "payment",
    "payment_link",
    "transaction_type",
    "amount",
    "transaction_key",
    "success",
    "reason",
    "raw_data",
    "created_at",
  ]

  fieldsets = (
    (
      "거래 기본 정보",
      {
        "fields": (
          "payment",
          "payment_link",
          "transaction_type",
          "amount",
          "success",
        )
      },
    ),
    (
      "거래 상세 정보",
      {
        "fields": (
          "transaction_key",
          "reason",
          "created_at",
        )
      },
    ),
    (
      "원본 데이터",
      {
        "fields": ("raw_data", ),
        "classes": ("collapse", ),
      },
    ),
  )
  list_filter_submit = True
  list_filter_sheet = False

  @admin.display(description="주문 ID", ordering="payment__order_id")
  def payment_order_id(self, obj):
    """결제 주문 ID 표시"""
    return obj.payment.order_id if obj.payment else "-"

  @admin.display(description="결제 링크")
  def payment_link(self, obj):
    """결제 상세 페이지 링크"""
    if obj.payment:
      url = f"/admin/payments/payment/{obj.payment.id}/change/"
      return format_html(
        '<a href="{}" target="_blank">결제 보기 ({})</a>',
        url,
        obj.payment.order_id,
      )
    return "-"

  @admin.display(description="거래 유형", ordering="transaction_type")
  def transaction_type_display(self, obj):
    """거래 유형 표시"""
    color_map = {
      "PAYMENT": "#4CAF50",
      "CANCEL": "#F44336",
      "PARTIAL_CANCEL": "#FF9800",
    }
    color = color_map.get(obj.transaction_type, "#000000")
    return format_html(
      '<span style="color: {}; font-weight: bold;">{}</span>',
      color,
      obj.get_transaction_type_display(),
    )

  @admin.display(description="금액", ordering="amount")
  def amount_display(self, obj):
    """금액 포맷"""
    color = "green" if obj.transaction_type == "PAYMENT" else "red"
    return format_html('<strong style="color: {};">{}원</strong>', color, f"{obj.amount:,}")

  @admin.display(description="성공 여부", ordering="success")
  def success_display(self, obj):
    """성공 여부 표시"""
    if obj.success:
      return format_html('<span style="color: green; font-weight: bold;">✓ 성공</span>')
    return format_html('<span style="color: red; font-weight: bold;">✗ 실패</span>')

  def has_add_permission(self, request):
    """거래 내역은 시스템에서만 생성 가능"""
    return False

  def has_change_permission(self, request, obj=None):
    """거래 내역은 수정 불가"""
    return False

  def has_delete_permission(self, request, obj=None):
    """거래 내역은 삭제 불가"""
    return False
