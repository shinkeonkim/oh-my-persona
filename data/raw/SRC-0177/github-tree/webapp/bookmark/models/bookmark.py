from config.models import BaseModel
from django.conf import settings
from django.db import models


class Bookmark(BaseModel):
    class Meta:
        db_table = "bookmarks"
        verbose_name = "bookmark"
        verbose_name_plural = "bookmarks"

    title = models.CharField(
        verbose_name="bookmark title", max_length=100, blank=False, null=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        related_name="bookmarks",
        on_delete=models.CASCADE,
    )

    bookmarkings_count = models.PositiveIntegerField(
        verbose_name="bookmarkings count",
        default=0,
    )

    def __str__(self):
        return self.title

    def reset_bookmarkings_count(self):
        self.bookmarkings_count = self.bookmarkings.count()
        self.save()
