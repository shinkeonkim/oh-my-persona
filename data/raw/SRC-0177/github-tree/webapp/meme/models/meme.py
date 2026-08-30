from config.models import BaseModelWithSoftDelete, SoftDeleteManager
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, QuerySet
from django.utils import timezone

TYPE_CHOICES = (
    ("Text", "Text"),
    ("Image", "Image"),
    ("Video", "Video"),
    ("Audio", "Audio"),
)


class MemeQuerySet(QuerySet):
    def preparing(self):
        return self.active().filter(published_at__isnull=True)

    def published(self):
        return self.active().filter(published_at__isnull=False)

    def active(self):
        return self.filter(archived_at__isnull=True)

    def archived(self):
        return self.filter(archived_at__isnull=False)


class MemeModelManager(SoftDeleteManager.from_queryset(MemeQuerySet)):
    use_for_related_fields = True

    def get_queryset(self):
        if self.model.MEME_TYPE == "":
            return super().get_queryset().all()
        return super().get_queryset().filter(type=self.model.MEME_TYPE)


class Meme(BaseModelWithSoftDelete):
    MEME_TYPE = ""

    class Meta:
        db_table = "memes"
        verbose_name = "meme"
        verbose_name_plural = "memes"

        indexes = [
            models.Index(fields=["type"]),
        ]

    objects = MemeModelManager()

    type = models.CharField(
        verbose_name="meme type",
        max_length=10,
        blank=False,
        null=False,
        choices=TYPE_CHOICES,
    )

    title = models.CharField(
        verbose_name="meme title", max_length=100, blank=False, null=False
    )

    # TODO(koa): title 컬럼에 대하여 GIN Index 도입
    # 데이터 및 쿼리에 따라 Full Text Search 확인 후 GIN Index 도입 여부 결정하기

    description = models.TextField(
        verbose_name="meme description", blank=False, null=False
    )

    original_link = models.URLField(
        verbose_name="original link",
        blank=True,
        null=True,
    )

    original_title = models.TextField(
        verbose_name="original title",
        max_length=100,
        blank=True,
        null=True,
    )

    published_at = models.DateTimeField(
        verbose_name="published at",
        blank=True,
        null=True,
    )

    archived_at = models.DateTimeField(
        verbose_name="archived at",
        blank=True,
        null=True,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creator",
        related_name="created_memes",
        on_delete=models.CASCADE,
    )

    tags = models.ManyToManyField(
        "tag.Tag",
        through="tag.MemeTagging",
        related_name="meme",
    )

    thumbnail = models.ForeignKey(
        "file_manager.Thumbnail",
        verbose_name="thumbnail",
        related_name="meme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    audio = models.ForeignKey(
        "file_manager.Audio",
        verbose_name="audio",
        related_name="meme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    video = models.ForeignKey(
        "file_manager.Video",
        verbose_name="video",
        related_name="meme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def related_memes(self):
        current_tag_ids = self.tags.values_list("id", flat=True)

        return (
            Meme.objects.filter(tags__in=current_tag_ids)
            .exclude(pk=self.pk)
            .annotate(
                common_tags_count=Count(
                    "tags", filter=models.Q(tags__in=current_tag_ids), distinct=True
                )
            )
            .order_by("-common_tags_count", "-published_at")
        )

    @property
    def bookmarking_users(self):
        user_model = get_user_model()
        return user_model.objects.filter(bookmarks__bookmarkings__meme=self).distinct()

    @property
    def views_count(self):
        return self.meme_counter.views_count

    @property
    def viewers_count(self):
        return self.meme_counter.viewers_count

    @property
    def bookmarking_users_count(self):
        return self.meme_counter.bookmarking_users_count

    @property
    def bookmarkings_count(self):
        return self.meme_counter.bookmarkings_count

    def bookmark_ids_by(self, user=None):
        if not user:
            return []

        return (
            user.bookmarkings.filter(meme=self, bookmark_id__isnull=False)
            .distinct()
            .order_by("bookmark_id")
            .values_list("bookmark_id", flat=True)
        )

    def __str__(self):
        return self.title

    def reset_all_counters(self):
        self.meme_counter.reset_all_counters()

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def archive(self):
        self.archived_at = timezone.now()
        self.save()

    def undo_publish(self):
        self.published_at = None
        self.save()

    def undo_archive(self):
        self.archived_at = None
        self.save()
