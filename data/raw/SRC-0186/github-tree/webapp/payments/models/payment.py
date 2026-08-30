from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import BaseModel


class PaymentStatus(models.TextChoices):
    """결제 상태"""

    READY = "READY", "결제 대기"
    IN_PROGRESS = "IN_PROGRESS", "결제 진행 중"
    WAITING_FOR_DEPOSIT = "WAITING_FOR_DEPOSIT", "입금 대기"
    DONE = "DONE", "결제 완료"
    CANCELED = "CANCELED", "결제 취소"
    PARTIAL_CANCELED = "PARTIAL_CANCELED", "부분 취소"
    ABORTED = "ABORTED", "결제 중단"
    EXPIRED = "EXPIRED", "결제 만료"


class Payment(BaseModel):
    """
    토스페이먼츠 결제 정보 모델

    Reference: https://docs.tosspayments.com/reference
    """

    # 기본 정보
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="사용자",
    )
    order_id = models.CharField(max_length=100, unique=True, verbose_name="주문 ID", db_index=True)
    order_name = models.CharField(max_length=255, verbose_name="주문명")
    amount = models.PositiveIntegerField(verbose_name="결제 금액")

    # 상품 정보 (Generic Relation for polymorphism)
    product_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="상품 타입",
        limit_choices_to=models.Q(app_label="payments"),
    )
    product_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="상품 ID",
    )
    product = GenericForeignKey("product_content_type", "product_object_id")

    # 캐싱 필드 (상품 삭제 시에도 결제 기록 유지를 위해)
    product_name = models.CharField(
        max_length=255,
        verbose_name="상품명",
        help_text="결제 시점의 상품명 (캐싱)",
    )

    # 티켓 상품 전용 캐싱 필드 (하위 호환성)
    ticket_quantity = models.PositiveIntegerField(
        default=0, verbose_name="구매 티켓 수량", help_text="티켓 상품인 경우에만 사용"
    )

    # 토스페이먼츠 정보
    payment_key = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="결제 키")
    secret = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="결제 Secret 키",
        help_text="웹훅 검증용 Secret 값",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.READY,
        verbose_name="결제 상태",
        db_index=True,
    )

    # 결제 수단 정보
    method = models.CharField(max_length=50, null=True, blank=True, verbose_name="결제 수단")
    method_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="결제 수단 상세")

    # 승인 정보
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="승인 일시")
    requested_at = models.DateTimeField(null=True, blank=True, verbose_name="요청 일시")

    # 영수증
    receipt_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="영수증 URL")

    # 환불 정보
    canceled_at = models.DateTimeField(null=True, blank=True, verbose_name="취소 일시")
    cancel_reason = models.TextField(null=True, blank=True, verbose_name="취소 사유")
    canceled_amount = models.PositiveIntegerField(default=0, verbose_name="취소된 금액")

    # 가상계좌 정보
    virtual_account_bank = models.CharField(max_length=50, null=True, blank=True, verbose_name="가상계좌 은행")
    virtual_account_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="가상계좌 번호")
    virtual_account_holder_name = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="가상계좌 예금주"
    )
    virtual_account_due_date = models.DateTimeField(null=True, blank=True, verbose_name="가상계좌 입금 기한")

    # 기타 정보
    customer_email = models.EmailField(max_length=255, null=True, blank=True, verbose_name="고객 이메일")
    customer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="고객 이름")
    customer_mobile_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="고객 휴대폰 번호")

    # 원본 응답 데이터 (JSON)
    raw_data = models.JSONField(null=True, blank=True, verbose_name="원본 응답 데이터")

    # 에러 정보
    fail_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="실패 코드")
    fail_message = models.TextField(null=True, blank=True, verbose_name="실패 메시지")

    class Meta:
        db_table = "payments"
        verbose_name = "결제"
        verbose_name_plural = "결제 목록"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} - {self.order_name} ({self.amount}원)"

    @property
    def refundable_amount(self):
        """환불 가능 금액"""
        return self.amount - self.canceled_amount

    @property
    def is_cancelable(self):
        """취소 가능 여부"""
        return self.status in [PaymentStatus.DONE, PaymentStatus.PARTIAL_CANCELED]
