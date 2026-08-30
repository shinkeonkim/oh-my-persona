from config.models import BaseModel, BaseModelManager
from django.conf import settings
from django.db import models


class Memo(BaseModel):
    class Meta:
        db_table = "memos"
        verbose_name = "memo"
        verbose_name_plural = "memos"

    objects = BaseModelManager()

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creator",
        on_delete=models.CASCADE,
        related_name="memos",
        blank=False,
        null=False,
    )

    meme = models.ForeignKey(
        "meme.Meme",
        verbose_name="meme",
        on_delete=models.CASCADE,
        related_name="memos",
        blank=False,
        null=False,
    )

    content = models.TextField(
        verbose_name="memo content",
        blank=False,
        null=False,
    )

    def __str__(self):
        return (
            f"Memo: {self.content[:20]}..."
            if len(self.content) > 20
            else f"Memo: {self.content}"
        )
