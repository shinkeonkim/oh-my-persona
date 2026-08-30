from django.db import models
from django.utils.translation import gettext_lazy as _


class GameCodeChoice(models.TextChoices):
    """
    게임 코드 Choice
    """

    BB_STAR = "BB_STAR", _("아기별 게임")
    KIDS_TRAFFIC = "KIDS_TRAFFIC", _("키즈 교통 게임")
