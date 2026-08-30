from abc import abstractmethod

from django.core.validators import MinValueValidator
from django.db import models

from common.models import BaseModel, BaseModelManager


class BaseProductQuerySet(models.QuerySet):
    def active(self):
        """판매 활성화된 상품만 반환"""
        return self.filter(is_active=True)


class BaseProductManager(BaseModelManager.from_queryset(BaseProductQuerySet)):
    pass


class BaseProduct(BaseModel):
    """
    결제 가능한 상품의 추상 베이스 모델

    모든 결제 가능한 상품은 이 클래스를 상속받아야 합니다.
    예: TicketProduct, SubscriptionProduct, DigitalContentProduct 등
    """

    objects = BaseProductManager()

    price = models.PositiveIntegerField(
        validators=[MinValueValidator(100)],
        verbose_name="가격 (KRW)",
        help_text="이 상품의 판매 가격 (원)",
    )
    discount_rate = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="할인율 (%)",
        help_text="표시용 할인율 (0-100)",
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="판매 활성화",
        help_text="이 상품의 판매 여부",
    )
    display_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="표시 순서",
        help_text="상품 목록에서의 표시 순서 (작을수록 먼저 표시)",
    )

    class Meta:
        abstract = True

    @abstractmethod
    def get_order_name(self) -> str:
        """
        주문명을 반환합니다.
        예: "티켓 10개 구매", "프리미엄 구독 1개월"
        """
        pass

    @abstractmethod
    def process_after_payment(self, payment):
        """
        결제 완료 후 처리할 로직을 구현합니다.
        예: 티켓 지급, 구독 활성화, 디지털 콘텐츠 접근 권한 부여 등

        Args:
            payment: Payment 객체
        """
        pass

    @abstractmethod
    def process_after_refund(self, payment, reason: str):
        """
        환불 완료 후 처리할 로직을 구현합니다.
        예: 티켓 회수, 구독 취소, 디지털 콘텐츠 접근 권한 제거 등

        Args:
            payment: Payment 객체
            reason: 환불 사유
        """
        pass

    @property
    def unit_price(self):
        """개당 단가 (기본 구현, 필요시 오버라이드)"""
        return self.price

    @property
    def original_price(self):
        """할인 전 원가 (기본 구현, 필요시 오버라이드)"""
        if self.discount_rate > 0:
            return int(self.price / (1 - self.discount_rate / 100))
        return self.price
