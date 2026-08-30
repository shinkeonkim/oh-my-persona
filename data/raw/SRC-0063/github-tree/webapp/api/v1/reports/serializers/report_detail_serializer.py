from reports.models import Report
from rest_framework import serializers

from api.v1.users.serializers import ChildSerializer

from .game_report_detail_serializer import GameReportDetailSerializer


class ReportDetailSerializer(serializers.ModelSerializer):
    """레포트 상세 정보 Serializer"""

    child = ChildSerializer(
        read_only=True,
    )
    game_reports = GameReportDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "child",
            "concentration_score",
            "game_reports",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
