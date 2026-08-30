from django.contrib import admin, messages
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
  AutocompleteSelectFilter,
  ChoicesDropdownFilter,
  RangeDateFilter,
  RelatedDropdownFilter,
)

from payments.models import Payment, Transaction
from payments.services.payment_service import PaymentService


class TransactionInline(admin.TabularInline):
  """거래 내역 인라인"""

  model = Transaction
  extra = 0
  readonly_fields = [
    "transaction_type",
    "amount",
    "transaction_key",
    "success",
    "reason",
    "created_at",
  ]
  can_delete = False

  def has_add_permission(self, request, obj=None):
    return False


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
  """결제 관리"""

  list_display = [
    "order_id",
    "user",
    "order_name",
    "amount_display",
    "product_info_display",
    "status_display",
    "method",
    "approved_at",
    "created_at",
  ]
  list_filter = [
    ("status", ChoicesDropdownFilter),
    ("method", ChoicesDropdownFilter),
    ("user", AutocompleteSelectFilter),
    ("product_content_type", RelatedDropdownFilter),
    ("created_at", RangeDateFilter),
    ("approved_at", RangeDateFilter),
  ]
  search_fields = [
    "order_id",
    "order_name",
    "product_name",
    "payment_key",
    "user__email",
    "customer_email",
  ]
  list_filter_submit = True
  list_filter_sheet = False
  autocomplete_fields = ["user"]
  readonly_fields = [
    "order_id",
    "payment_key",
    "product_content_type",
    "product_object_id",
    "product_name",
    "product_link",
    "ticket_quantity",
    "approved_at",
    "requested_at",
    "canceled_at",
    "receipt_url_link",
    "refundable_amount_display",
    "raw_data",
    "created_at",
    "updated_at",
  ]
  inlines = [TransactionInline]
  actions = ["cancel_payments"]

  fieldsets = (
    (
      "기본 정보",
      {
        "fields": (
          "user",
          "order_id",
          "order_name",
          "amount",
          "status",
        )
      },
    ),
    (
      "상품 정보",
      {
        "fields": (
          "product_content_type",
          "product_object_id",
          "product_name",
          "product_link",
          "ticket_quantity",
        )
      },
    ),
    (
      "결제 수단",
      {
        "fields": (
          "method",
          "method_type",
          "payment_key",
        )
      },
    ),
    (
      "승인 정보",
      {
        "fields": (
          "approved_at",
          "requested_at",
          "receipt_url_link",
        )
      },
    ),
    (
      "취소 정보",
      {
        "fields": (
          "canceled_at",
          "cancel_reason",
          "canceled_amount",
          "refundable_amount_display",
        )
      },
    ),
    (
      "가상계좌 정보",
      {
        "fields": (
          "virtual_account_bank",
          "virtual_account_number",
          "virtual_account_holder_name",
          "virtual_account_due_date",
        ),
        "classes": ("collapse", ),
      },
    ),
    (
      "고객 정보",
      {
        "fields": (
          "customer_email",
          "customer_name",
          "customer_mobile_phone",
        )
      },
    ),
    (
      "에러 정보",
      {
        "fields": (
          "fail_code",
          "fail_message",
        ),
        "classes": ("collapse", ),
      },
    ),
    (
      "기타",
      {
        "fields": (
          "raw_data",
          "created_at",
          "updated_at",
        ),
        "classes": ("collapse", ),
      },
    ),
  )

  @admin.display(description="금액", ordering="amount")
  def amount_display(self, obj):
    """금액 포맷"""
    return format_html("<strong>{}원</strong>", f"{obj.amount:,}")

  @admin.display(description="상품 정보")
  def product_info_display(self, obj):
    """상품 정보 표시"""
    if obj.product_content_type:
      product_type = obj.product_content_type.model
      return format_html(
        '<span style="color: #666;">{}</span> #{}<br/><small>{}</small>',
        product_type,
        obj.product_object_id,
        obj.product_name,
      )
    return "-"

  @admin.display(description="상품 링크")
  def product_link(self, obj):
    """상품 상세 페이지 링크"""
    if obj.product:
      url = (f"/admin/{obj.product_content_type.app_label}/" +
             f"{obj.product_content_type.model}/{obj.product_object_id}/change/")
      return format_html(
        '<a href="{}" target="_blank">{} 보기</a>',
        url,
        obj.product_content_type.model,
      )
    return "-"

  @admin.display(description="상태", ordering="status")
  def status_display(self, obj):
    """상태 표시"""
    color_map = {
      "READY": "#FFA500",
      "IN_PROGRESS": "#2196F3",
      "WAITING_FOR_DEPOSIT": "#9C27B0",
      "DONE": "#4CAF50",
      "CANCELED": "#F44336",
      "PARTIAL_CANCELED": "#FF9800",
      "ABORTED": "#757575",
      "EXPIRED": "#9E9E9E",
    }
    color = color_map.get(obj.status, "#000000")
    return format_html(
      '<span style="color: {}; font-weight: bold;">{}</span>',
      color,
      obj.get_status_display(),
    )

  @admin.display(description="영수증")
  def receipt_url_link(self, obj):
    """영수증 URL 링크"""
    if obj.receipt_url:
      return format_html('<a href="{}" target="_blank">영수증 보기</a>', obj.receipt_url)
    return "-"

  @admin.display(description="환불 가능 금액")
  def refundable_amount_display(self, obj):
    """환불 가능 금액 표시"""
    if obj.refundable_amount > 0:
      return format_html(
        '<strong style="color: green;">{}원</strong>',
        f"{obj.refundable_amount:,}",
      )
    return format_html('<span style="color: gray;">0원</span>')

  @admin.action(description="선택한 결제 취소하기")
  def cancel_payments(self, request, queryset):
    """결제 취소 액션"""
    payment_service = PaymentService()
    success_count = 0
    error_count = 0

    for payment in queryset:
      try:
        if not payment.is_cancelable:
          self.message_user(
            request,
            f"'{payment.order_id}' - 취소 불가능한 상태입니다: {payment.get_status_display()}",
            level=messages.WARNING,
          )
          error_count += 1
          continue

        # 관리자가 취소하는 경우 기본 사유 제공
        cancel_reason = "관리자에 의한 결제 취소"
        payment_service.cancel_payment(payment, cancel_reason)
        success_count += 1

      except Exception as e:
        self.message_user(
          request,
          f"'{payment.order_id}' 취소 실패: {str(e)}",
          level=messages.ERROR,
        )
        error_count += 1

    if success_count > 0:
      self.message_user(
        request,
        f"{success_count}건의 결제가 성공적으로 취소되었습니다.",
        level=messages.SUCCESS,
      )
    if error_count > 0:
      self.message_user(
        request,
        f"{error_count}건의 결제 취소에 실패했습니다.",
        level=messages.ERROR,
      )

  def has_add_permission(self, request):
    """결제는 시스템에서만 생성 가능"""
    return False

  def has_delete_permission(self, request, obj=None):
    """결제 기록은 삭제 불가"""
    return False
