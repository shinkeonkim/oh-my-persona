from django.conf import settings

from rest_framework import serializers

from payments.models import Payment

from .transaction_serializer import TransactionSerializer


class PaymentDetailSerializer(serializers.ModelSerializer):
    """결제 정보 (상세)"""

    refundable_amount = serializers.IntegerField(read_only=True)
    is_cancelable = serializers.BooleanField(read_only=True)
    product_type = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source="product_object_id", read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    client_key = serializers.SerializerMethodField()
    success_url = serializers.SerializerMethodField()
    fail_url = serializers.SerializerMethodField()

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
            "method_type",
            "payment_key",
            "approved_at",
            "requested_at",
            "canceled_at",
            "cancel_reason",
            "canceled_amount",
            "refundable_amount",
            "is_cancelable",
            "receipt_url",
            "virtual_account_bank",
            "virtual_account_number",
            "virtual_account_holder_name",
            "virtual_account_due_date",
            "customer_email",
            "customer_name",
            "customer_mobile_phone",
            "fail_code",
            "fail_message",
            "transactions",
            "client_key",
            "success_url",
            "fail_url",
            "created_at",
            "updated_at",
        ]

    def get_product_type(self, obj):
        """상품 타입 반환"""
        if obj.product_content_type:
            return obj.product_content_type.model
        return None

    def get_client_key(self, obj):
        """토스페이먼츠 클라이언트 키 반환"""
        return settings.TOSS_PAYMENTS_CLIENT_KEY

    def get_success_url(self, obj):
        """결제 성공 URL 반환"""
        return settings.TOSS_PAYMENTS_SUCCESS_URL

    def get_fail_url(self, obj):
        """결제 실패 URL 반환"""
        return settings.TOSS_PAYMENTS_FAIL_URL
