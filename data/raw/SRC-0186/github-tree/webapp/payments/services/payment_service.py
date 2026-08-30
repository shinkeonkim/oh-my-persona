import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from payments.models import Payment, PaymentStatus, Transaction, TransactionType

from .toss_payments_client import TossPaymentsClient

User = get_user_model()
logger = logging.getLogger(__name__)


class PaymentService:
    """결제 서비스"""

    def __init__(self):
        self.client = TossPaymentsClient()

    def create_payment(
        self,
        user: User,
        product_type: str,
        product_id: int,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_mobile_phone: Optional[str] = None,
    ) -> Payment:
        """
        상품 구매를 위한 결제 준비

        Args:
            user: 사용자
            product_type: 상품 타입 (예: 'ticketproduct', 'subscriptionproduct')
            product_id: 구매할 상품 ID
            customer_email: 고객 이메일
            customer_name: 고객 이름
            customer_mobile_phone: 고객 휴대폰 번호

        Returns:
            Payment 객체
        """
        from django.contrib.contenttypes.models import ContentType

        from payments.models import BaseProduct

        # ContentType 조회
        try:
            content_type = ContentType.objects.get(app_label="payments", model=product_type.lower())
        except ContentType.DoesNotExist:
            raise ValueError(f"존재하지 않는 상품 타입입니다: {product_type}")

        # 상품 조회
        model_class = content_type.model_class()
        if not issubclass(model_class, BaseProduct):
            raise ValueError(f"결제 가능한 상품이 아닙니다: {product_type}")

        try:
            product = model_class.objects.active().get(id=product_id)
        except model_class.DoesNotExist:
            raise ValueError(f"존재하지 않거나 판매 중단된 상품입니다: {product_type}#{product_id}")

        # 상품 정보로 결제 정보 생성
        amount = product.price
        order_name = product.get_order_name()

        # 고유한 주문 ID 생성
        order_id = self._generate_order_id()

        # Payment 생성
        payment = Payment.objects.create(
            user=user,
            order_id=order_id,
            order_name=order_name,
            amount=amount,
            product_content_type=content_type,
            product_object_id=product_id,
            product_name=order_name,  # 캐싱
            status=PaymentStatus.READY,
            customer_email=customer_email or user.email,
            customer_name=customer_name,
            customer_mobile_phone=customer_mobile_phone,
        )

        # 티켓 상품인 경우 ticket_quantity 캐싱 (하위 호환성)
        if product_type.lower() == "ticketproduct":
            from payments.models import TicketProduct

            if isinstance(product, TicketProduct):
                payment.ticket_quantity = product.quantity
                payment.save(update_fields=["ticket_quantity"])

        logger.info(f"결제 준비 완료: {order_id}, " f"상품: {product_type}#{product_id}, " f"금액: {amount}원")
        return payment

    @transaction.atomic
    def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> Payment:
        """
        결제 승인

        Args:
            payment_key: 결제 키
            order_id: 주문 ID
            amount: 결제 금액

        Returns:
            Payment 객체
        """
        try:
            # 결제 정보 조회
            payment = Payment.objects.select_for_update().get(order_id=order_id)

            # 금액 검증
            if payment.amount != amount:
                raise ValueError(f"결제 금액이 일치하지 않습니다. 요청: {amount}원, 실제: {payment.amount}원")

            # 이미 승인된 결제인지 확인
            if payment.status == PaymentStatus.DONE:
                logger.warning(f"이미 승인된 결제: {order_id}")
                return payment

            # 토스페이먼츠 API 호출
            response = self.client.confirm_payment(payment_key, order_id, amount)

            # 에러 응답 처리
            if "code" in response:
                payment.status = PaymentStatus.ABORTED
                payment.fail_code = response.get("code")
                payment.fail_message = response.get("message")
                payment.raw_data = response
                payment.save()

                # 실패 거래 기록
                Transaction.objects.create(
                    payment=payment,
                    transaction_type=TransactionType.PAYMENT,
                    amount=amount,
                    success=False,
                    reason=response.get("message"),
                    raw_data=response,
                )

                raise ValueError(f"결제 승인 실패: {response.get('code')} - {response.get('message')}")

            # 결제 정보 업데이트
            payment.payment_key = payment_key
            payment.secret = response.get("secret")  # 웹훅 검증용 secret 저장
            payment.status = PaymentStatus.DONE
            payment.method = response.get("method")
            payment.method_type = response.get("type")
            payment.approved_at = self._parse_datetime(response.get("approvedAt"))
            payment.requested_at = self._parse_datetime(response.get("requestedAt"))
            payment.receipt_url = response.get("receipt", {}).get("url")
            payment.raw_data = response

            # 가상계좌 정보 저장
            if payment.method == "가상계좌":
                virtual_account = response.get("virtualAccount", {})
                payment.virtual_account_bank = virtual_account.get("bankCode")
                payment.virtual_account_number = virtual_account.get("accountNumber")
                payment.virtual_account_holder_name = virtual_account.get("customerName")
                payment.virtual_account_due_date = self._parse_datetime(virtual_account.get("dueDate"))
                payment.status = PaymentStatus.WAITING_FOR_DEPOSIT

            payment.save()

            # 성공 거래 기록
            Transaction.objects.create(
                payment=payment,
                transaction_type=TransactionType.PAYMENT,
                amount=amount,
                transaction_key=payment_key,
                success=True,
                raw_data=response,
            )

            # 결제 완료 시 상품별 후처리 (가상계좌는 입금 대기 상태이므로 제외)
            if payment.status == PaymentStatus.DONE and payment.product:
                self._process_after_payment(payment)

            logger.info(f"결제 승인 완료: {order_id}, 금액: {amount}원")
            return payment

        except Payment.DoesNotExist:
            logger.error(f"결제 정보를 찾을 수 없습니다: {order_id}")
            raise ValueError(f"결제 정보를 찾을 수 없습니다: {order_id}")
        except Exception as e:
            logger.error(f"결제 승인 중 오류 발생: {e}")
            raise

    @transaction.atomic
    def cancel_payment(
        self,
        payment: Payment,
        cancel_reason: str,
        cancel_amount: Optional[int] = None,
    ) -> Payment:
        """
        결제 취소

        Args:
            payment: Payment 객체
            cancel_reason: 취소 사유
            cancel_amount: 취소 금액 (부분 취소 시)

        Returns:
            Payment 객체
        """
        if not payment.is_cancelable:
            raise ValueError(f"취소할 수 없는 결제 상태입니다: {payment.status}")

        if not payment.payment_key:
            raise ValueError("결제 키가 없습니다")

        # 부분 취소 금액 검증
        if cancel_amount is not None:
            if cancel_amount > payment.refundable_amount:
                raise ValueError(
                    f"취소 금액이 환불 가능 금액을 초과합니다. "
                    f"요청: {cancel_amount}원, 가능: {payment.refundable_amount}원"
                )

        try:
            # 토스페이먼츠 API 호출
            response = self.client.cancel_payment(payment.payment_key, cancel_reason, cancel_amount)

            # 취소 정보 업데이트
            cancels = response.get("cancels", [])
            if cancels:
                latest_cancel = cancels[-1]
                payment.canceled_at = self._parse_datetime(latest_cancel.get("canceledAt"))
                payment.cancel_reason = latest_cancel.get("cancelReason")

            # 전체 취소된 금액 계산
            total_canceled = sum(cancel.get("cancelAmount", 0) for cancel in cancels)
            payment.canceled_amount = total_canceled

            # 상태 업데이트
            if total_canceled >= payment.amount:
                payment.status = PaymentStatus.CANCELED
            else:
                payment.status = PaymentStatus.PARTIAL_CANCELED

            payment.raw_data = response
            payment.save()

            # 취소 거래 기록
            transaction_type = (
                TransactionType.CANCEL if total_canceled >= payment.amount else TransactionType.PARTIAL_CANCEL
            )

            Transaction.objects.create(
                payment=payment,
                transaction_type=transaction_type,
                amount=cancel_amount or payment.amount,
                success=True,
                reason=cancel_reason,
                raw_data=response,
            )

            # 결제 취소 시 상품별 환불 처리 (전액 취소인 경우만)
            if payment.status == PaymentStatus.CANCELED and payment.product:
                self._process_after_refund(payment, cancel_reason)

            logger.info(f"결제 취소 완료: {payment.order_id}, 취소 금액: {cancel_amount or payment.amount}원")
            return payment

        except Exception as e:
            logger.error(f"결제 취소 중 오류 발생: {e}")
            raise

    def get_payment_info(self, payment: Payment) -> Dict[str, Any]:
        """
        결제 정보 조회

        Args:
            payment: Payment 객체

        Returns:
            결제 정보
        """
        if not payment.payment_key:
            return {
                "order_id": payment.order_id,
                "order_name": payment.order_name,
                "amount": payment.amount,
                "status": payment.status,
            }

        try:
            response = self.client.get_payment(payment.payment_key)
            return response
        except Exception as e:
            logger.error(f"결제 정보 조회 중 오류 발생: {e}")
            raise

    def _generate_order_id(self) -> str:
        """고유한 주문 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"ORDER-{timestamp}-{unique_id}"

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """ISO 8601 형식의 날짜 문자열을 datetime 객체로 변환"""
        if not datetime_str:
            return None

        try:
            # ISO 8601 형식: 2024-10-24T12:00:00+09:00
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.error(f"날짜 변환 실패: {datetime_str}, {e}")
            return None

    def _process_after_payment(self, payment: Payment) -> None:
        """
        결제 완료 후 상품별 후처리

        Args:
            payment: Payment 객체
        """
        try:
            product = payment.product
            if product and hasattr(product, "process_after_payment"):
                product.process_after_payment(payment)
                logger.info(
                    f"결제 후처리 완료: {payment.order_id}, "
                    f"상품: {payment.product_content_type.model}#{payment.product_object_id}"
                )
            else:
                logger.warning(f"상품이 없거나 후처리 메서드가 없습니다: {payment.order_id}")
        except Exception as e:
            logger.error(f"결제 후처리 실패: {payment.order_id}, 에러: {e}")
            raise

    def _process_after_refund(self, payment: Payment, reason: str) -> None:
        """
        환불 완료 후 상품별 환불 처리

        Args:
            payment: Payment 객체
            reason: 환불 사유
        """
        try:
            product = payment.product
            if product and hasattr(product, "process_after_refund"):
                product.process_after_refund(payment, reason)
                logger.info(
                    f"환불 후처리 완료: {payment.order_id}, "
                    f"상품: {payment.product_content_type.model}#{payment.product_object_id}"
                )
            else:
                logger.warning(f"상품이 없거나 환불 후처리 메서드가 없습니다: {payment.order_id}")
        except Exception as e:
            logger.error(f"환불 후처리 실패: {payment.order_id}, 에러: {e}")
            raise
