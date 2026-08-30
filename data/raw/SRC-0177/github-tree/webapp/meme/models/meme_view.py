from config.models import BaseModel, BaseModelManager
from django.conf import settings
from django.db import models


class MemeView(BaseModel):
    class Meta:
        db_table = "meme_views"
        verbose_name = "meme_view"
        verbose_name_plural = "meme_views"
        unique_together = ("meme", "user")
        indexes = [
            models.Index(fields=["meme", "user"]),
        ]

    objects = BaseModelManager()

    meme = models.ForeignKey(
        "meme.Meme",
        on_delete=models.CASCADE,
        related_name="meme_views",
        null=False,
        blank=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meme_views",
        null=False,
        blank=False,
    )
    count = models.IntegerField(
        default=0,
        null=False,
        blank=False,
    )
