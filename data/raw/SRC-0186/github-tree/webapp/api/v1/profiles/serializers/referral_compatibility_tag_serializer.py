from rest_framework import serializers

from matchmakings.models import CompatibilityTag


class ReferralCompatibilityTagSerializer(serializers.ModelSerializer):
  """추천 궁합 태그 시리얼라이저"""

  class Meta:
    model = CompatibilityTag
    fields = [
      "id",
      "name",
    ]
    read_only_fields = [
      "id",
      "name",
    ]
