from config.models import BaseModelWithSoftDelete, SoftDeleteManager
from django.db import models
from django.utils.html import format_html


class Thumbnail(BaseModelWithSoftDelete):
    class Meta:
        db_table = "thumbnails"
        verbose_name = "thumbnail"
        verbose_name_plural = "thumbnails"

    objects = SoftDeleteManager()

    name = models.CharField(
        max_length=255,
        verbose_name="이름",
        null=False,
        blank=False,
        default="thumbnail",
    )

    file = models.ImageField(
        upload_to="thumbnails/",
        verbose_name="썸네일 파일",
        null=True,
        blank=True,
    )

    web_url = models.URLField(
        verbose_name="웹 URL",
        help_text="웹에서 접근할 수 있는 URL, 파일이 없는 경우 사용됩니다.",
        null=True,
        blank=True,
        max_length=500,
    )

    @property
    def url(self):
        if self.file:
            return self.file.url

        return self.web_url

    @property
    def preview_image(self):
        return format_html(
            '<img src="{}" style="max-width:200px; max-height:200px"/>'.format(self.url)
        )

    def __str__(self):
        return self.name
