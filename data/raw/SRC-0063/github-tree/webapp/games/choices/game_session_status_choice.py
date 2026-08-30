from django.db import models
from django.utils.translation import gettext_lazy as _


class GameSessionStatusChoice(models.TextChoices):
    """
    게임 세션 상태 Choice
    """

    STARTED = "STARTED", _("시작")
    COMPLETED = "COMPLETED", _("완료")
    GAME_OVER = "GAME_OVER", _("게임 오버")
    FORFEIT = "FORFEIT", _("포기")
