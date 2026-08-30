from django.db import models
from django.utils.translation import gettext_lazy as _

from games.choices import GameCodeChoice

from common.models import BaseModel, BaseModelManager


class GameManager(BaseModelManager):
    def active(self):
        return self.filter(is_active=True)

    def by_code(self, code):
        return self.filter(code=code)


class Game(BaseModel):
    """
    게임 모델
    """

    class Meta:
        db_table = "games"
        verbose_name = _("게임")
        verbose_name_plural = _("게임")
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_game_code"),
        ]

    objects = GameManager()

    code = models.CharField(
        max_length=32,
        choices=GameCodeChoice.choices,
        null=False,
        blank=False,
        unique=True,
        verbose_name=_("게임 코드"),
        help_text="게임 고유 코드 (BB_STAR, KIDS_TRAFFIC 등)",
    )
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_("표시명"),
    )
    max_round = models.IntegerField(
        default=10,
        verbose_name=_("최대 라운드"),
        help_text="게임의 최대 라운드 수 (기본값: 10)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("사용 여부"),
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
