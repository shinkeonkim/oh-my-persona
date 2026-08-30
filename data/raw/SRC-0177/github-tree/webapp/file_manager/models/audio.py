from config.models import BaseModelWithSoftDelete
from django.db import models


class Audio(BaseModelWithSoftDelete):
    class Meta:
        db_table = "audios"
        verbose_name = "audio"
        verbose_name_plural = "audios"

    name = models.CharField(
        max_length=255,
        verbose_name="이름",
        null=False,
        blank=False,
        default="audio",
    )

    file = models.FileField(
        upload_to="audios/",
        verbose_name="파일",
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.file.url
