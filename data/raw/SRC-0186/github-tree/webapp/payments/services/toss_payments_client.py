import base64
import logging
from typing import Any, Dict, Optional

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class TossPaymentsClient:
    """
    토스페이먼츠 API 클라이언트

    Reference: https://docs.tosspayments.com/reference/using-api/api-keys
    """

    def __init__(self):
        self.api_url = settings.TOSS_PAYMENTS_API_URL
        self.secret_key = settings.TOSS_PAYMENTS_SECRET_KEY
        self.client_key = settings.TOSS_PAYMENTS_CLIENT_KEY

    def _get_headers(self) -> Dict[str, str]:
        """API 호출에 필요한 헤더 생성"""
        # Basic 인증: secret_key를 Base64로 인코딩
        auth_string = f"{self.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
        }

    def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> Dict[str, Any]:
        """
        결제 승인

        Args:
            payment_key: 결제 키
            order_id: 주문 ID
            amount: 결제 금액

        Returns:
            승인된 결제 정보

        Reference: https://docs.tosspayments.com/guides/v2/payment-widget/integration
        """
        url = f"{self.api_url}/payments/confirm"
        payload = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount,
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"결제 승인 실패: {e}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"에러 응답: {error_data}")
                    return error_data
                except Exception:
                    pass
            raise

    def get_payment(self, payment_key: str) -> Dict[str, Any]:
        """
        결제 조회

        Args:
            payment_key: 결제 키

        Returns:
            결제 정보

        Reference: https://docs.tosspayments.com/reference#payment-조회
        """
        url = f"{self.api_url}/payments/{payment_key}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"결제 조회 실패: {e}")
            raise

    def cancel_payment(
        self, payment_key: str, cancel_reason: str, cancel_amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        결제 취소

        Args:
            payment_key: 결제 키
            cancel_reason: 취소 사유
            cancel_amount: 취소 금액 (부분 취소 시)

        Returns:
            취소된 결제 정보

        Reference: https://docs.tosspayments.com/guides/v2/cancel-payment
        """
        url = f"{self.api_url}/payments/{payment_key}/cancel"
        payload = {"cancelReason": cancel_reason}

        if cancel_amount is not None:
            payload["cancelAmount"] = cancel_amount

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"결제 취소 실패: {e}")
            raise

    def get_payment_by_order_id(self, order_id: str) -> Dict[str, Any]:
        """
        주문 ID로 결제 조회

        Args:
            order_id: 주문 ID

        Returns:
            결제 정보

        Reference: https://docs.tosspayments.com/reference#payment-주문-id로-조회
        """
        url = f"{self.api_url}/payments/orders/{order_id}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"결제 조회 실패 (order_id={order_id}): {e}")
            raise
