from config.models import BaseModelWithSoftDelete
from django.db import models
from django.db.models import Q


class MemeTagging(BaseModelWithSoftDelete):
    class Meta:
        db_table = "meme_taggings"
        verbose_name = "meme_tagging"
        verbose_name_plural = "meme_taggings"
        indexes = [models.Index(fields=["meme", "tag"])]
        constraints = [
            models.UniqueConstraint(
                fields=["meme", "tag"],
                name="unique_meme_tag",
                condition=Q(deleted_at__isnull=True),
            )
        ]

    meme = models.ForeignKey(
        "meme.Meme",
        on_delete=models.CASCADE,
        related_name="meme_taggings",
    )

    tag = models.ForeignKey(
        "tag.Tag",
        on_delete=models.CASCADE,
        related_name="meme_taggings",
    )

    def __str__(self):
        return f"{self.meme} - {self.tag}"
