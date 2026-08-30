from rest_framework import serializers

from api.v1.profiles.serializers.user_profile_list_serializer import (
  UserProfileListSerializer,
)
from matchmakings.models import Matching


class MatchingListSerializer(serializers.ModelSerializer):
  """Matching 목록 시리얼라이저"""

  sender = UserProfileListSerializer(read_only=True)
  receiver = UserProfileListSerializer(read_only=True)

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
      "expired_at",
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
      "expired_at",
    ]
