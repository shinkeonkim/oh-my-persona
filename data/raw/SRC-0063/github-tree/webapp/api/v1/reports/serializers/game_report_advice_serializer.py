from reports.models import GameReportAdvice
from rest_framework import serializers


class GameReportAdviceSerializer(serializers.ModelSerializer):
    """게임 레포트 조언 Serializer"""

    class Meta:
        model = GameReportAdvice
        fields = [
            "id",
            "title",
            "description",
            "created_at",
        ]
        read_only_fields = fields
