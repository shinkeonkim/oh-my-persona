from config.models import BaseModel, BaseModelManager
from django.db import models
from django.db.models import QuerySet


class BookmarkingQuerySet(QuerySet):
    def with_bookmark(self):
        return self.filter(bookmark_id__isnull=False)

    def without_bookmark(self):
        return self.filter(bookmark_id__isnull=True)


class BookmarkingModelManager(BaseModelManager.from_queryset(BookmarkingQuerySet)):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().all()


class Bookmarking(BaseModel):
    class Meta:
        db_table = "bookmarkings"
        verbose_name = "bookmarking"
        verbose_name_plural = "bookmarkings"
        indexes = [
            models.Index(fields=["meme", "bookmark"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "meme", "bookmark"],
                name="unique_user_meme_bookmark",
            ),
        ]

    objects = BookmarkingModelManager()

    bookmark = models.ForeignKey(
        "bookmark.Bookmark",
        verbose_name="bookmark",
        related_name="bookmarkings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    meme = models.ForeignKey(
        "meme.Meme",
        verbose_name="meme",
        related_name="bookmarkings",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    user = models.ForeignKey(
        "user.User",
        verbose_name="user",
        related_name="bookmarkings",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.bookmark} - {self.meme}"

    def save(self, *args, **kwargs):
        if self.bookmark is not None:
            self.user = self.bookmark.user
        super().save(*args, **kwargs)
