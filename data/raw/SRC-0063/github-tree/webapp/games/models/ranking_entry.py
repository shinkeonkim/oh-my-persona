from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel, BaseModelManager


class RankingEntryManager(BaseModelManager):
    def by_game(self, game):
        return self.filter(game=game)

    def top_scores(self, game, limit=10):
        """게임별 상위 점수 조회"""
        return self.filter(game=game).order_by("-score", "-round_count", "created_at").select_related("game")[:limit]

    def get_top_score(self, game):
        """게임별 최고점 조회"""
        top_entry = self.top_scores(game, limit=1).first()
        return top_entry.score if top_entry else 0


class RankingEntry(BaseModel):
    """
    랭킹 엔트리 모델
    데모부스 이벤트용 게임 랭킹을 저장
    """

    class Meta:
        db_table = "ranking_entries"
        verbose_name = _("랭킹 엔트리")
        verbose_name_plural = _("랭킹 엔트리")
        ordering = ["-score", "-round_count", "created_at"]
        indexes = [
            models.Index(fields=["game", "-score"]),
        ]

    objects = RankingEntryManager()

    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="ranking_entries",
        null=False,
        blank=False,
        verbose_name=_("게임"),
    )
    game_result = models.ForeignKey(
        "games.GameResult",
        on_delete=models.SET_NULL,
        related_name="ranking_entry",
        null=True,
        blank=True,
        verbose_name=_("게임 결과"),
        help_text="연결된 게임 결과 (선택적)",
    )
    player_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_("참가자 이름"),
        help_text="데모부스에서 입력한 참가자 이름",
    )
    score = models.IntegerField(
        null=False,
        blank=False,
        verbose_name=_("점수"),
        help_text="게임 점수",
    )
    round_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("도달한 라운드"),
        help_text="도달한 최종 라운드 수",
    )
    contact_info = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("연락처"),
        help_text="참가자 연락처 (선택)",
    )
    organization = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_("소속"),
        help_text="참가자 소속 (학교, 회사 등)",
    )
    is_event_highlighted = models.BooleanField(
        default=False,
        verbose_name=_("이벤트 하이라이트"),
        help_text="최고점 갱신 시 이벤트 표시 여부",
    )
    event_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("이벤트 발생 시각"),
        help_text="최고점 갱신 이벤트가 발생한 시각",
    )

    def __str__(self):
        return f"{self.player_name} - {self.game.name} (점수: {self.score})"
