from django.db import models
from django.utils.translation import gettext_lazy as _


class ReportStatusChoice(models.TextChoices):
    NO_GAMES_PLAYED = "no_games_played", _("게임 미플레이")
    PENDING = "pending", _("대기 중")
    GENERATING = "generating", _("진행 중")
    COMPLETED = "completed", _("완료")
    ERROR = "error", _("오류 발생")
