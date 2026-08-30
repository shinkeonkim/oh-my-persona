from drf_spectacular.utils import extend_schema_field
from reports.models import GameReport
from rest_framework import serializers

from .game_report_advice_serializer import GameReportAdviceSerializer


class GameReportDetailSerializer(serializers.ModelSerializer):
    """게임 레포트 Serializer"""

    game_name = serializers.CharField(
        source="game.name",
        read_only=True,
    )
    game_code = serializers.CharField(
        source="game.code",
        read_only=True,
    )
    last_reflected_session_id = serializers.UUIDField(
        source="last_reflected_session.id",
        read_only=True,
        allow_null=True,
    )
    is_up_to_date = serializers.SerializerMethodField()
    advices = GameReportAdviceSerializer(
        many=True,
        read_only=True,
    )

    # 계산된 통계 필드
    total_reaction_ms_avg = serializers.SerializerMethodField()
    wrong_rate = serializers.SerializerMethodField()
    avg_rounds_count = serializers.SerializerMethodField()
    max_rounds_ratio = serializers.FloatField(
        source="get_max_rounds_ratio",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = GameReport
        fields = [
            "id",
            "game_name",
            "game_code",
            "last_reflected_session_id",
            "is_up_to_date",
            # 통계 컬럼
            "total_plays_count",
            "total_play_rounds_count",
            "max_rounds_count",
            "total_reaction_ms_sum",
            "total_play_actions_count",
            "total_success_count",
            "total_wrong_count",
            # 계산된 통계
            "total_reaction_ms_avg",
            "wrong_rate",
            "avg_rounds_count",
            "max_rounds_ratio",
            # LLM 기반 데이터
            "advices",
            # 타임스탬프
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.BooleanField)
    def get_is_up_to_date(self, obj) -> bool:
        """게임 레포트가 최신 상태인지 확인"""
        return obj.is_up_to_date()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_total_reaction_ms_avg(self, obj) -> int | None:
        """평균 반응시간"""
        return obj.get_total_reaction_ms_avg()

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_wrong_rate(self, obj) -> float | None:
        """오답률"""
        return obj.get_wrong_rate()

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_avg_rounds_count(self, obj) -> float | None:
        """평균 도달 라운드"""
        return obj.get_avg_rounds_count()

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_max_rounds_ratio(self, obj) -> float | None:
        """최대 라운드 도달 비율"""
        return obj.get_max_rounds_ratio()
