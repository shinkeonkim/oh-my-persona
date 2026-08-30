from django.db import models

from common.models import BaseModel


class CompatibilityTag(BaseModel):
    class Meta:
        db_table = "compatibility_tags"
        verbose_name = "Compatibility Tag"
        verbose_name_plural = "Compatibility Tags"

    name = models.CharField(max_length=255, verbose_name="태그 이름")
