import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from games.choices import GameSessionStatusChoice

from common.models import BaseModel, BaseModelManager

User = get_user_model()


class GameSessionManager(BaseModelManager):
    def active(self):
        return self.filter(status=GameSessionStatusChoice.STARTED)

    def by_parent(self, parent):
        return self.filter(parent=parent)

    def by_child(self, child):
        return self.filter(child=child)


class GameSession(BaseModel):
    """
    게임 세션 모델
    게임 진행 상황을 추적
    """

    class Meta:
        db_table = "game_sessions"
        verbose_name = _("게임 세션")
        verbose_name_plural = _("게임 세션")
        ordering = ["-started_at"]

    objects = GameSessionManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("세션 ID"),
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="game_sessions",
        null=False,
        blank=False,
        verbose_name=_("부모"),
    )
    child = models.ForeignKey(
        "users.Child",
        on_delete=models.CASCADE,
        related_name="game_sessions",
        null=False,
        blank=False,
        verbose_name=_("아동"),
    )
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="game_sessions",
        null=False,
        blank=False,
        verbose_name=_("게임"),
    )
    status = models.CharField(
        max_length=16,
        choices=GameSessionStatusChoice.choices,
        default=GameSessionStatusChoice.STARTED,
        null=False,
        blank=False,
        verbose_name=_("상태"),
    )
    current_round = models.SmallIntegerField(
        default=1,
        null=False,
        blank=False,
        verbose_name=_("현재 라운드"),
    )
    current_score = models.IntegerField(
        default=0,
        null=False,
        blank=False,
        verbose_name=_("진행 중 누계 점수"),
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        verbose_name=_("시작 시각"),
    )
    ended_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("종료 시각"),
    )
    meta = models.JSONField(
        blank=True,
        default=dict,
        null=True,
        verbose_name=_("메타데이터"),
        help_text="라운드 진행상태 등 임시 값",
    )

    def __str__(self):
        return f"{self.child.name} - {self.game.name} (라운드 {self.current_round})"
