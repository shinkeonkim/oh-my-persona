from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderChoice(models.TextChoices):
    MALE = "M", _("남자")
    FEMALE = "F", _("여자")
    NO_CHOICE = "X", _("선택 안함")
