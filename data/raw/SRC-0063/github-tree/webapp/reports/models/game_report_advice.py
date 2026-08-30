from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel, BaseModelManager


class GameReportAdviceManager(BaseModelManager):
    def by_game_report(self, game_report):
        return self.filter(game_report=game_report)

    def by_game(self, game):
        return self.filter(game=game)


class GameReportAdvice(BaseModel):
    """
    게임 레포트 조언 모델
    LLM을 통한 게임 결과 분석 및 조언
    """

    class Meta:
        db_table = "game_report_advices"
        verbose_name = _("게임 레포트 조언")
        verbose_name_plural = _("게임 레포트 조언")
        ordering = ["-created_at"]

    objects = GameReportAdviceManager()

    game_report = models.ForeignKey(
        "reports.GameReport",
        on_delete=models.CASCADE,
        related_name="advices",
        null=False,
        blank=False,
        verbose_name=_("게임 레포트"),
    )
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="report_advices",
        null=False,
        blank=False,
        verbose_name=_("게임"),
    )
    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name=_("제목"),
        help_text="조언 제목",
    )
    description = models.TextField(
        null=False,
        blank=False,
        verbose_name=_("설명"),
        help_text="조언 상세 내용",
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("오류 메시지"),
        help_text="조언 생성 중 발생한 오류 메시지",
    )

    def __str__(self):
        return f"{self.game_report} - {self.title}"
