from rest_framework import serializers


class CompatibilityScoreSerializer(serializers.Serializer):
  """추천 궁합 점수 시리얼라이저"""

  compatibility_score = serializers.IntegerField(help_text="궁합 점수 (0-100)")
