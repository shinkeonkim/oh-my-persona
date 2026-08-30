from rest_framework import serializers


class MatchingCreateSerializer(serializers.Serializer):
    """매칭 생성 시리얼라이저"""

    referral_id = serializers.IntegerField(help_text="추천 ID")
