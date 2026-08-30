import logging

from django.conf import settings
from django.db import models

from users.services.ticket_service import TicketService

from .base_product import BaseProduct, BaseProductManager

logger = logging.getLogger(__name__)
KRW_PRICE_PER_TICKET = settings.KRW_PRICE_PER_TICKET


class TicketProductManager(BaseProductManager):
    pass


class TicketProduct(BaseProduct):
    """
    티켓 상품 모델
    어드민을 통해 티켓 수량과 가격을 관리합니다.
    """

    class Meta:
        db_table = "ticket_products"
        verbose_name = "티켓 상품"
        verbose_name_plural = "티켓 상품 목록"
        ordering = ["display_order", "quantity"]

    objects = TicketProductManager()

    quantity = models.PositiveIntegerField(
        unique=True,
        verbose_name="티켓 수량",
        help_text="이 상품으로 구매할 수 있는 티켓 수량",
    )

    def __str__(self):
        return f"티켓 {self.quantity}개 - {self.price:,}원"

    def get_order_name(self) -> str:
        """주문명 반환"""
        return f"티켓 {self.quantity}개 구매"

    def process_after_payment(self, payment):
        """결제 완료 후 티켓 지급"""
        try:
            ticket_service = TicketService(payment.user)

            ticket_service.purchase_tickets(
                amount=self.quantity,
                payment=payment,
                description=f"결제 완료: {payment.order_name} ({payment.order_id})",
            )

            logger.info(
                f"티켓 지급 완료: {payment.order_id}, " f"사용자: {payment.user.email}, " f"수량: {self.quantity}개"
            )
        except Exception as e:
            logger.error(f"티켓 지급 실패: {payment.order_id}, 에러: {e}")
            raise

    def process_after_refund(self, payment, reason: str):
        """환불 완료 후 티켓 회수"""
        from users.models.ticket_log import TicketLog, TicketLogCategory

        try:
            # 이 결제로 지급된 티켓 로그 확인
            ticket_logs = payment.ticket_logs.filter(category=TicketLogCategory.PURCHASE)

            if not ticket_logs.exists():
                logger.warning(f"환불할 티켓 로그가 없습니다: {payment.order_id}")
                return

            # 사용자의 티켓을 차감
            user = payment.user
            if user.ticket_amount < self.quantity:
                logger.warning(
                    f"환불할 티켓이 부족합니다: {payment.order_id}, "
                    f"필요: {self.quantity}, "
                    f"보유: {user.ticket_amount}"
                )
                raise ValueError("환불에 필요한 티켓이 부족합니다.")
            else:
                refund_amount = self.quantity

            if refund_amount > 0:
                user.ticket_amount -= refund_amount
                user.save(update_fields=["ticket_amount"])

                # 환불 로그 생성
                TicketLog.objects.create(
                    user=user,
                    amount=refund_amount,
                    category=TicketLogCategory.REFUND,
                    description=f"결제 취소로 인한 환불: {payment.order_name} ({reason})",
                    payment=payment,
                )

                logger.info(
                    f"티켓 환불 완료: {payment.order_id}, " f"사용자: {user.email}, " f"수량: {refund_amount}개"
                )
        except Exception as e:
            logger.error(f"티켓 환불 실패: {payment.order_id}, 에러: {e}")
            raise

    @property
    def unit_price(self):
        """개당 단가"""
        return self.price // self.quantity if self.quantity > 0 else 0

    @property
    def original_price(self):
        """할인 전 원가 (기본 단가 기준)"""
        return self.quantity * KRW_PRICE_PER_TICKET

    def save(self, *args, **kwargs):
        """할인율 자동 계산"""
        if self.quantity > 0:
            original = self.quantity * KRW_PRICE_PER_TICKET
            if original > 0:
                self.discount_rate = int(((original - self.price) / original) * 100)
        super().save(*args, **kwargs)
