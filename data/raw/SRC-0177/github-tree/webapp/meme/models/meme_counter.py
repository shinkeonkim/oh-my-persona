from config.models import BaseModel, BaseModelManager
from django.db import models


class MemeCounter(BaseModel):
    class Meta:
        db_table = "meme_counters"
        verbose_name = "meme_counter"
        verbose_name_plural = "meme_counters"

    objects = BaseModelManager()

    meme = models.OneToOneField(
        "meme.Meme", on_delete=models.CASCADE, related_name="meme_counter"
    )
    bookmarking_users_count = models.PositiveIntegerField(
        default=0, null=False, blank=False, help_text="북마크한 유저 수"
    )
    bookmarkings_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="북마크 수 (북마크한 유저 수와 다를 수 있음, 한 유저가 중복 북마크 가능)",
    )

    views_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="조회 수",
    )

    viewers_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="조회자 수",
    )

    def reset_all_counters(self):
        self.reset_bookmarking_users_count()
        self.reset_bookmarkings_count()

    def reset_bookmarking_users_count(self):
        self.bookmarking_users_count = self.meme.bookmarking_users.count()
        self.save()

    def reset_bookmarkings_count(self):
        self.bookmarkings_count = self.meme.bookmarkings.count()
        self.save()
