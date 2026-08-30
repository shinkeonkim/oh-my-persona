from .base import GameFinishSerializer, GameStartSerializer


class BBStarStartSerializer(GameStartSerializer):
    """뿅뿅 아기별 게임 시작 Serializer"""

    pass


class BBStarFinishSerializer(GameFinishSerializer):
    """뿅뿅 아기별 게임 종료 Serializer (시간 관련 필드 제외)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # reaction_ms_sum 필드 제거
        self.fields.pop("reaction_ms_sum", None)
