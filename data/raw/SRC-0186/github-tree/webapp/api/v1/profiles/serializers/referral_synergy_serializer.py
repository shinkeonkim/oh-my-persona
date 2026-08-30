from rest_framework import serializers

from matchmakings.models import ReferralSynergy


class ReferralSynergySerializer(serializers.ModelSerializer):
  """추천 천생연분 시너지 시리얼라이저"""

  class Meta:
    model = ReferralSynergy
    fields = [
      "id",
      "title",
      "description",
      "generation_status",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "title",
      "description",
      "generation_status",
      "created_at",
      "updated_at",
    ]
