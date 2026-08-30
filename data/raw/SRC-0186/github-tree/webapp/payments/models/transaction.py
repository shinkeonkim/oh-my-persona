from django.db import models

from common.models import BaseModel

from .payment import Payment


class TransactionType(models.TextChoices):
    """거래 유형"""

    PAYMENT = "PAYMENT", "결제"
    CANCEL = "CANCEL", "취소"
    PARTIAL_CANCEL = "PARTIAL_CANCEL", "부분 취소"


class Transaction(BaseModel):
    """
    결제 거래 내역 모델
    결제, 취소 등 모든 거래를 기록
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="결제",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name="거래 유형",
        db_index=True,
    )
    amount = models.PositiveIntegerField(verbose_name="거래 금액")
    transaction_key = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="거래 키")

    # 거래 상태
    success = models.BooleanField(default=False, verbose_name="성공 여부")

    # 거래 세부 정보
    reason = models.TextField(null=True, blank=True, verbose_name="사유")

    # 원본 응답 데이터
    raw_data = models.JSONField(null=True, blank=True, verbose_name="원본 응답 데이터")

    class Meta:
        db_table = "payment_transactions"
        verbose_name = "결제 거래"
        verbose_name_plural = "결제 거래 목록"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.payment.order_id} - {self.transaction_type} ({self.amount}원)"
