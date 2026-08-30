from rest_framework import serializers


class PaymentCreateSerializer(serializers.Serializer):
    """결제 준비 요청"""

    product_type = serializers.CharField(
        max_length=50,
        help_text="상품 타입 (예: 'ticketproduct', 'subscriptionproduct')",
    )
    product_id = serializers.IntegerField(
        min_value=1,
        help_text="구매할 상품 ID",
    )
    customer_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="고객 이메일",
    )
    customer_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="고객 이름",
    )
    customer_mobile_phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="고객 휴대폰 번호",
    )
