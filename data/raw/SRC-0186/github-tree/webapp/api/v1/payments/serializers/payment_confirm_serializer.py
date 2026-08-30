from rest_framework import serializers


class PaymentConfirmSerializer(serializers.Serializer):
    """결제 승인 요청"""

    payment_key = serializers.CharField(max_length=200, help_text="결제 키")
    order_id = serializers.CharField(max_length=100, help_text="주문 ID")
    amount = serializers.IntegerField(
        min_value=100,
        help_text="결제 금액",
    )
