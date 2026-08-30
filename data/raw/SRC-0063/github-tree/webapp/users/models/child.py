from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel, BaseModelManager
from users.choices import GenderChoice

from .user import User


class ChildManager(BaseModelManager):
    pass


class Child(BaseModel):
    """
    자녀 모델
    """

    class Meta:
        db_table = "children"
        verbose_name = _("자녀")
        verbose_name_plural = _("자녀")

    objects = ChildManager()

    parent = models.OneToOneField(User, on_delete=models.CASCADE, related_name="child")
    name = models.CharField(
        verbose_name=_("이름"),
        null=False,
        blank=False,
        max_length=50,
    )
    birth_year = models.PositiveSmallIntegerField(
        verbose_name=_("생년"),
        null=False,
        blank=False,
        validators=[MinValueValidator(1900)],
    )
    gender = models.CharField(
        max_length=1,
        choices=GenderChoice.choices,
        default=GenderChoice.NO_CHOICE,
        null=False,
        blank=False,
    )
