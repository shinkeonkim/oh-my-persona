from rest_framework import serializers


class GameStartSerializer(serializers.Serializer):
    """게임 시작 공통 Serializer"""

    pass


class GameStartResponseSerializer(serializers.Serializer):
    """게임 시작 응답 공통 Serializer"""

    session_id = serializers.UUIDField(
        read_only=True,
        help_text="게임 세션 고유 식별자 (UUID). 게임 종료 API 호출 시 필요",
    )
    game_code = serializers.CharField(
        read_only=True,
        help_text="게임 코드 (예: 'BB_STAR', 'KIDS_TRAFFIC')",
    )
    started_at = serializers.DateTimeField(
        read_only=True,
        help_text="게임 세션 시작 시각 (ISO 8601 형식)",
    )
    status = serializers.CharField(
        read_only=True,
        help_text="게임 세션 상태 (예: 'STARTED')",
    )


class GameFinishSerializer(serializers.Serializer):
    """
    게임 종료 공통 Serializer

    프론트에서 보내는 정보:
    1. meta 외 필드 (전체 게임 집계 정보):
       - session_id, score, wrong_count, reaction_ms_sum, round_count, success_count

    2. meta 필드 (라운드별 상세 데이터):
       - round_details: 각 라운드의 상세 정보

    meta 필드 구조 예시 (각 라운드별 상세 정보):
    {
        "round_details": [
            {
                "round_number": 1,
                "score": 10,                    # 해당 라운드 점수
                "wrong_count": 1,               # 해당 라운드 틀린 개수
                "reaction_ms_sum": 1500,   # 해당 라운드 반응시간 합계
                "is_success": True,             # 해당 라운드 성공 여부
                "time_limit_exceeded": False    # 제한시간 초과 여부
            },
            {
                "round_number": 2,
                "score": 5,
                "wrong_count": 2,
                "reaction_ms_sum": 2000,
                "is_success": False,
                "time_limit_exceeded": True
            },
            ...
        ]
    }

    """

    session_id = serializers.UUIDField(
        required=True,
        help_text="게임 시작 API에서 받은 세션 ID (UUID). 게임 종료 시 필요",
    )
    score = serializers.IntegerField(
        required=True,
        help_text="게임 전체 총 점수 (Integer). 모든 라운드에서 획득한 점수의 합계",
    )
    wrong_count = serializers.IntegerField(
        required=False,
        default=0,
        help_text="게임 전체 틀린 개수 (Integer, 기본값: 0). 모든 라운드에서 발생한 오답의 총합",
    )
    reaction_ms_sum = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="게임 전체 반응시간 합계 (Integer, 밀리초 단위). 모든 라운드의 반응시간을 합산 "
        "뿅뿅아기별 게임에서는 사용 X",
    )
    round_count = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="게임 전체 라운드 수 (Integer). 플레이한 총 라운드 수(최대 10라운드)",
    )
    success_count = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="게임 전체 성공한 라운드 수 (Integer). 성공적으로 완료한 라운드의 개수",
    )
    meta = serializers.JSONField(
        required=False,
        allow_null=True,
        default=dict,
        help_text=(
            "라운드별 상세 데이터 (JSON 객체). 각 라운드의 상세 정보를 포함\n\n"
            "구조:\n"
            "{\n"
            "  'round_details': [\n"
            "    {\n"
            "      'round_number': 1,              # 라운드 번호 (1부터 시작)\n"
            "      'score': 10,                    # 해당 라운드에서 획득한 점수\n"
            "      'wrong_count': 1,              # 해당 라운드에서 틀린 횟수\n"
            "      'reaction_ms_sum': 1500,       # 해당 라운드 반응시간 합계 (밀리초, 교통지킴이만)\n"
            "      'is_success': true,            # 해당 라운드 성공 여부 (boolean)\n"
            "      'time_limit_exceeded': false   # 제한시간 초과 여부 (boolean)\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "참고: 뿅뿅아기별 게임의 round_details에는 'reaction_ms_sum' 필드가 없음"
        ),
    )


class BaseGameFinishResponseSerializer(serializers.Serializer):
    """게임 종료 응답 기본 Serializer (공통 필드)"""

    session_id = serializers.UUIDField(
        read_only=True,
        help_text="게임 세션 고유 식별자 (UUID)",
    )
    game_code = serializers.CharField(
        read_only=True,
        help_text="게임 코드",
    )
    score = serializers.IntegerField(
        read_only=True,
        help_text="게임 전체 총 점수 (Integer)",
    )
    wrong_count = serializers.IntegerField(
        read_only=True,
        help_text="게임 전체 틀린 개수 (Integer)",
    )
    round_count = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        help_text="게임 전체 라운드 수 (Integer, 최대 10라운드)",
    )
    success_count = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        help_text="게임 전체 성공한 라운드 수 (Integer)",
    )
    meta = serializers.JSONField(
        read_only=True,
        allow_null=True,
        help_text="라운드별 상세 데이터 (JSON 객체)",
    )


class GameFinishResponseSerializer(BaseGameFinishResponseSerializer):
    """게임 종료 응답 공통 Serializer (모든 필드 포함)"""

    reaction_ms_sum = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        help_text="게임 전체 반응시간 합계 (Integer, 밀리초 단위)",
    )


class BBStarFinishResponseSerializer(BaseGameFinishResponseSerializer):
    """뿅뿅 아기별 게임 종료 응답 Serializer (시간 관련 필드 제외)"""

    game_code = serializers.CharField(
        read_only=True,
        help_text="게임 코드 ('BB_STAR')",
    )
    meta = serializers.JSONField(
        read_only=True,
        allow_null=True,
        help_text="라운드별 상세 데이터 (JSON 객체). 뿅뿅아기별 게임은 시간 측정이 없으므로 "
        "round_details에 'reaction_ms_sum' 필드가 포함되지 않음",
    )


class KidsTrafficFinishResponseSerializer(BaseGameFinishResponseSerializer):
    """꼬마 교통지킴이 게임 종료 응답 Serializer"""

    game_code = serializers.CharField(
        read_only=True,
        help_text="게임 코드 ('KIDS_TRAFFIC')",
    )
    wrong_count = serializers.IntegerField(
        read_only=True,
        help_text="게임 전체 틀린 개수 (Integer). 신호등에 맞지 않는 버튼을 누른 횟수",
    )
    reaction_ms_sum = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        help_text="게임 전체 반응시간 합계 (Integer, 밀리초 단위). " "신호등 변화에 대한 반응 시간을 측정한 값",
    )
    meta = serializers.JSONField(
        read_only=True,
        allow_null=True,
        help_text="라운드별 상세 데이터 (JSON 객체). 각 라운드의 반응시간 정보가 포함",
    )
