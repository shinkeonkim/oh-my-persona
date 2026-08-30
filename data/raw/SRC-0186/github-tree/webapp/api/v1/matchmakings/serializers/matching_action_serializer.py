from rest_framework import serializers


class MatchingActionSerializer(serializers.Serializer):
    """Matching 액션 (승인/거부) 시리얼라이저"""

    action = serializers.ChoiceField(
        choices=[
            ("accept", "승인"),
            ("reject", "거부"),
        ],
        help_text="매칭 액션: accept(승인) 또는 reject(거부)",
    )
