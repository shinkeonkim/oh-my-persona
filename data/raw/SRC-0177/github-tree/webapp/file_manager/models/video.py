from config.models import BaseModelWithSoftDelete
from django.core.exceptions import ValidationError
from django.db import models

TYPE_CHOICES = (
    ("Youtube", "Youtube"),
    ("Facebook", "Facebook"),
    ("Instagram", "Instagram"),
    ("X", "X"),
    ("Vimeo", "Vimeo"),
)


class Video(BaseModelWithSoftDelete):
    class Meta:
        db_table = "videos"
        verbose_name = "video"
        verbose_name_plural = "videos"

    name = models.CharField(
        max_length=255,
        verbose_name="이름",
        null=False,
        blank=False,
        default="video",
    )

    file = models.FileField(
        upload_to="videos/",
        verbose_name="파일",
        null=True,
        blank=True,
    )

    link = models.URLField(
        verbose_name="영상 링크",
        null=True,
        blank=True,
    )

    link_type = models.CharField(
        max_length=20,
        verbose_name="링크 타입 (영상 링크 출처)",
        choices=TYPE_CHOICES,
        null=True,
        blank=True,
    )  # TODO: 내부 사용자 - 사용성 개선 : 링크 보고 자동으로 타입 지정하면 더 좋을 것 같다.

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.file.url

    @property
    def type(self):
        return "file" if self.file else "link"

    def clean(self):
        self.validate_video_data()

    def validate_video_data(self):
        if self.file or self.link:
            return

        raise ValidationError(
            {"file": "비디오 파일 또는 링크 중 하나는 반드시 입력해야 합니다."}
        )
