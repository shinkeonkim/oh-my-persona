from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel, BaseModelManager

User = get_user_model()


class GameResultManager(BaseModelManager):
    def by_child(self, child):
        return self.filter(child=child)

    def by_game(self, game):
        return self.filter(game=game)


class GameResult(BaseModel):
    """
    게임 결과 모델
    완료된 게임 세션의 최종 결과를 저장
    """

    class Meta:
        db_table = "game_results"
        verbose_name = _("게임 결과")
        verbose_name_plural = _("게임 결과")
        constraints = [
            models.UniqueConstraint(fields=["session"], name="unique_session_result"),
        ]
        ordering = ["-created_at"]

    objects = GameResultManager()

    session = models.OneToOneField(
        "games.GameSession",
        on_delete=models.CASCADE,
        related_name="result",
        null=False,
        blank=False,
        db_column="session_id",
        verbose_name=_("게임 세션"),
    )
    child = models.ForeignKey(
        "users.Child",
        on_delete=models.CASCADE,
        related_name="game_results",
        null=False,
        blank=False,
        verbose_name=_("아동"),
    )
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="game_results",
        null=False,
        blank=False,
        verbose_name=_("게임"),
    )
    score = models.IntegerField(
        null=False,
        blank=False,
        verbose_name=_("총점"),
    )
    wrong_count = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name=_("오답 수"),
    )
    reaction_ms_sum = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("반응 시간 합계(ms)"),
        help_text="모든 반응 시간의 합계",
    )
    round_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("라운드 수"),
        help_text="완료한 라운드 수",
    )
    success_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("성공 횟수"),
        help_text="성공한 횟수",
    )
    meta = models.JSONField(
        blank=True,
        default=dict,
        null=True,
        verbose_name=_("메타데이터"),
        help_text="라운드별 상세 데이터",
    )

    def __str__(self):
        id = self.id if self.id else "Unsaved"
        child_name = self.child.name if self.child else "Unknown Child"
        game_name = self.game.name if self.game else "Unknown Game"
        date = self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "Unsaved"
        return f"[{id}] {child_name} - {game_name} (점수: {self.score}) ({date})"
