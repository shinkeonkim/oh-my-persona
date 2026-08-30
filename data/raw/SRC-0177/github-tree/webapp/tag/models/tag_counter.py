from config.models import BaseModel, BaseModelManager
from django.db import models


class TagCounter(BaseModel):
    class Meta:
        db_table = "tag_counters"
        verbose_name = "tag_counter"
        verbose_name_plural = "tag_counters"

    objects = BaseModelManager()

    tag = models.OneToOneField(
        "tag.Tag", on_delete=models.CASCADE, related_name="tag_counter"
    )

    memes_count = models.PositiveIntegerField(
        default=0, null=False, blank=False, help_text="태그가 적용된 밈 수"
    )

    bookmarkings_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="태그가 적용된 밈들의 총 북마크 수",
    )

    def reset_all_counters(self):
        self.reset_memes_count()
        self.reset_bookmarkings_count()
        self.save()

    def reset_memes_count(self):
        self.memes_count = self.tag.meme_taggings.filter(
            deleted_at__isnull=True
        ).count()
        self.save()

    def reset_bookmarkings_count(self):
        from meme.models import Meme

        meme_ids = self.tag.meme_taggings.filter(deleted_at__isnull=True).values_list(
            "meme_id", flat=True
        )

        self.bookmarkings_count = (
            Meme.objects.filter(id__in=meme_ids).aggregate(
                total_bookmarkings=models.Sum("meme_counter__bookmarkings_count")
            )["total_bookmarkings"]
            or 0
        )

        self.save()
