from rest_framework import serializers

from payments.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """거래 내역"""

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "transaction_key",
            "success",
            "reason",
            "created_at",
        ]
