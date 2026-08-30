from rest_framework import serializers

from payments.models import TicketProduct


class TicketProductSerializer(serializers.ModelSerializer):
    """티켓 상품 정보"""

    unit_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = TicketProduct
        fields = [
            "id",
            "quantity",
            "price",
            "unit_price",
            "discount_rate",
            "display_order",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "quantity",
            "price",
            "discount_rate",
            "unit_price",
        ]
