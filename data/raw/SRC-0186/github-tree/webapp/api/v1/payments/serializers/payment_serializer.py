from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """결제 정보 (목록용)"""

    refundable_amount = serializers.IntegerField(read_only=True)
    is_cancelable = serializers.BooleanField(read_only=True)
    product_type = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source="product_object_id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "order_name",
            "amount",
            "product_type",
            "product_id",
            "product_name",
            "ticket_quantity",
            "status",
            "method",
            "payment_key",
            "approved_at",
            "canceled_at",
            "canceled_amount",
            "refundable_amount",
            "is_cancelable",
            "receipt_url",
            "created_at",
            "updated_at",
        ]

    def get_product_type(self, obj):
        """상품 타입 반환"""
        if obj.product_content_type:
            return obj.product_content_type.model
        return None
