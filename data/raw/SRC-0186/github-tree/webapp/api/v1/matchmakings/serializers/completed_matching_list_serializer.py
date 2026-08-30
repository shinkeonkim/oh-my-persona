from rest_framework import serializers

from api.v1.profiles.serializers import (
    CompletedMatchingUserProfileListSerializer,
)
from matchmakings.models import Matching


class CompletedMatchingListSerializer(serializers.ModelSerializer):
    """매칭 완료 목록 시리얼라이저"""

    sender = CompletedMatchingUserProfileListSerializer(read_only=True)
    receiver = CompletedMatchingUserProfileListSerializer(read_only=True)

    class Meta:
        model = Matching
        fields = [
            "id",
            "sender",
            "receiver",
            "status",
            "ticket_amount",
            "sent_at",
            "received_at",
            "rejected_at",
        ]
        read_only_fields = [
            "id",
            "sender",
            "receiver",
            "status",
            "ticket_amount",
            "sent_at",
            "received_at",
            "rejected_at",
        ]
