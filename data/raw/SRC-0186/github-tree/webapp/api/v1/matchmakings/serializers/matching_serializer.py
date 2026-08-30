from rest_framework import serializers

from api.v1.profiles.serializers.user_profile_serializer import UserProfileSerializer
from matchmakings.models import Matching


class MatchingSerializer(serializers.ModelSerializer):
  """Matching 상세 정보 시리얼라이저"""

  sender = UserProfileSerializer(read_only=True)
  receiver = UserProfileSerializer(read_only=True)
  status = serializers.CharField(read_only=True)

  class Meta:
    model = Matching
    fields = [
      "id",
      "sender",
      "receiver",
      "referral_id",
      "ticket_amount",
      "sent_at",
      "received_at",
      "rejected_at",
      "expired_at",
      "status",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "sender",
      "receiver",
      "referral_id",
      "ticket_amount",
      "sent_at",
      "received_at",
      "rejected_at",
      "expired_at",
      "created_at",
      "updated_at",
    ]
