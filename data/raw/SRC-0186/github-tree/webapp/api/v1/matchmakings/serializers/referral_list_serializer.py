from rest_framework import serializers

from api.v1.profiles.serializers.user_profile_list_serializer import (
  UserProfileListSerializer,
)
from matchmakings.models import Referral


class ReferralListSerializer(serializers.ModelSerializer):
  """Referral 목록 시리얼라이저"""

  user = UserProfileListSerializer(read_only=True)
  referral_user = UserProfileListSerializer(read_only=True)

  class Meta:
    model = Referral
    fields = [
      "id",
      "user",
      "referral_user",
      "referred_at",
    ]
    read_only_fields = [
      "id",
      "user",
      "referral_user",
      "referred_at",
    ]
