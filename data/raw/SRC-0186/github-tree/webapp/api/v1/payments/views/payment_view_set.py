from django.db import transaction

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.payments.serializers import (
    PaymentConfirmSerializer,
    PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentSerializer,
)
from common.utils.logger import get_logger
from common.views import BaseViewSet
from payments.models import Payment, PaymentStatus
from payments.services import PaymentService

logger = get_logger(__name__)


@extend_schema_view(
    list=extend_schema(summary="결제 목록 조회", tags=["Payments"]),
    retrieve=extend_schema(summary="결제 상세 조회", tags=["Payments"]),
    create=extend_schema(summary="결제 준비", tags=["Payments"]),
)
class PaymentViewSet(BaseViewSet):
    """결제 관리 ViewSet"""

    serializer_class = PaymentSerializer
    http_method_names = ["get", "post"]  # PUT, PATCH, DELETE 비활성화

    def get_queryset(self):
        """사용자의 결제 목록만 조회"""
        return Payment.objects.filter(user=self.current_user).prefetch_related("transactions")

    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == "retrieve":
            return PaymentDetailSerializer
        elif self.action == "create":
            return PaymentCreateSerializer
        elif self.action == "confirm":
            return PaymentConfirmSerializer
        return PaymentSerializer

    @extend_schema(
        summary="결제 준비",
        description="티켓 구매를 위한 결제를 준비하고 주문 ID와 클라이언트 키를 반환합니다.",
        tags=["Payments"],
        request=PaymentCreateSerializer,
        responses={201: PaymentDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        """결제 준비"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_service = PaymentService()
        payment = payment_service.create_payment(user=self.current_user, **serializer.validated_data)

        # 클라이언트에 필요한 정보 반환 (client_key, success_url, fail_url은 serializer에서 자동으로 포함됨)
        return Response(PaymentDetailSerializer(payment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="결제 승인",
        description="토스페이먼츠에서 받은 결제 정보를 검증하고 승인합니다. 승인 완료 시 자동으로 티켓이 지급됩니다.",
        tags=["Payments"],
        request=PaymentConfirmSerializer,
        responses={200: PaymentDetailSerializer},
    )
    @action(detail=False, methods=["post"], url_path="confirm")
    def confirm(self, request):
        """결제 승인"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_service = PaymentService()

        try:
            payment = payment_service.confirm_payment(**serializer.validated_data)
            return Response(PaymentDetailSerializer(payment).data, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error(f"결제 승인 실패: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"결제 승인 중 오류 발생: {e}")
            return Response(
                {"error": "결제 승인 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="웹훅 처리",
        description="토스페이먼츠에서 보내는 웹훅을 처리합니다. (가상계좌 입금 등)",
        tags=["Payments"],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="webhook",
        permission_classes=[],
    )
    def webhook(self, request):
        """웹훅 처리 - Secret 검증 포함"""
        logger.info(f"웹훅 수신: {request.data}")

        # 웹훅 데이터 파싱
        event_type = request.data.get("eventType")
        data = request.data.get("data", {})

        if event_type == "PAYMENT_STATUS_CHANGED":
            # 결제 상태 변경 처리
            order_id = data.get("orderId")
            status_value = data.get("status")
            webhook_secret = data.get("secret")

            try:
                payment = Payment.objects.select_for_update().get(order_id=order_id)

                # Secret 검증
                if not self._verify_webhook_secret(payment, webhook_secret):
                    logger.error(
                        f"웹훅 Secret 검증 실패: {order_id}, "
                        f"저장된 secret: {payment.secret}, "
                        f"웹훅 secret: {webhook_secret}"
                    )

                    # 검증 실패 시 이미 처리된 결제가 있다면 롤백
                    if payment.status == PaymentStatus.DONE:
                        self._rollback_payment(payment, "웹훅 Secret 검증 실패")

                    return Response(
                        {"error": "Invalid webhook secret"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                # 가상계좌 입금 완료 시 상품별 후처리
                if status_value == "DONE" and payment.status != "DONE":
                    payment.status = status_value
                    payment.raw_data = data
                    payment.save()

                    # 상품별 후처리 (티켓 지급 등)
                    if payment.product:
                        payment_service = PaymentService()
                        payment_service._process_after_payment(payment)
                else:
                    payment.status = status_value
                    payment.raw_data = data
                    payment.save()

                logger.info(f"웹훅 처리 완료: {order_id}, 상태: {status_value}")
                return Response({"success": True}, status=status.HTTP_200_OK)
            except Payment.DoesNotExist:
                logger.error(f"결제 정보를 찾을 수 없습니다: {order_id}")
                return Response(
                    {"error": "Payment not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                logger.error(f"웹훅 처리 중 오류 발생: {order_id}, 에러: {e}")
                return Response(
                    {"error": "Internal server error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            logger.warning(f"처리되지 않은 웹훅 이벤트: {event_type}")
            return Response({"success": True}, status=status.HTTP_200_OK)

    def _verify_webhook_secret(self, payment: Payment, webhook_secret: str) -> bool:
        """
        웹훅 Secret 검증

        Args:
            payment: Payment 객체
            webhook_secret: 웹훅으로 받은 secret 값

        Returns:
            검증 성공 여부
        """
        if not payment.secret:
            logger.warning(f"결제에 저장된 secret이 없습니다: {payment.order_id}")
            return False

        if not webhook_secret:
            logger.warning(f"웹훅에 secret이 포함되지 않았습니다: {payment.order_id}")
            return False

        return payment.secret == webhook_secret

    def _rollback_payment(self, payment: Payment, reason: str) -> None:
        """
        검증 실패 시 결제 롤백

        Args:
            payment: Payment 객체
            reason: 롤백 사유
        """
        try:
            with transaction.atomic():
                # 이미 지급된 상품이 있다면 환불 처리
                if payment.product and hasattr(payment.product, "process_after_refund"):
                    payment.product.process_after_refund(payment, reason)

                # 결제 상태를 ABORTED로 변경
                original_status = payment.status
                payment.status = PaymentStatus.ABORTED
                payment.fail_code = "WEBHOOK_VERIFICATION_FAILED"
                payment.fail_message = reason
                payment.save()

                logger.warning(
                    f"결제 롤백 완료: {payment.order_id}, " f"이전 상태: {original_status}, " f"사유: {reason}"
                )
        except Exception as e:
            logger.error(f"결제 롤백 실패: {payment.order_id}, 에러: {e}")
            raise
