from config.models import BaseModel, BaseModelManager
from config.settings.base import AUTH_USER_MODEL
from django.db import models
from django.db.models import Count, Q
from tag.models import Tag


class TagUserCounter(BaseModel):
    class Meta:
        db_table = "tag_user_counters"
        verbose_name = "tag_user_counter"
        verbose_name_plural = "tag_user_counters"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tag"], name="unique_tag_user_counter"
            )
        ]

    objects = BaseModelManager()

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tag_counters"
    )

    tag = models.ForeignKey(
        "tag.Tag", on_delete=models.CASCADE, related_name="user_tag_counters"
    )

    bookmarks_count = models.PositiveIntegerField(default=0, null=False, blank=False)

    bookmarkings_count = models.PositiveIntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return f"{self.user.email} - {self.tag.name} - {self.bookmarks_count} - {self.bookmarkings_count}"

    @classmethod
    def reset_all_counters(cls, user):
        # 북마크가 있는 경우와 없는 경우 모두 고려
        tag_counts_qs = Tag.objects.filter(meme__bookmarkings__user=user).annotate(
            bc=Count("meme__bookmarkings", filter=Q(meme__bookmarkings__user=user)),
            bkc=Count(
                "meme__bookmarkings__bookmark",
                filter=Q(
                    meme__bookmarkings__bookmark__isnull=False,
                    meme__bookmarkings__user=user,
                ),
            ),
        )

        rows = []
        for tag in tag_counts_qs:
            rows.append(
                {
                    "user_id": user.pk,
                    "tag_id": tag.pk,
                    "bookmarkings_count": tag.bc,
                    "bookmarks_count": tag.bkc,
                }
            )

        cls.objects.bulk_upsert(
            conflict_target=["user", "tag"],
            rows=rows,
            return_model=False,
        )

    @classmethod
    def reset_counter_for_tag(cls, user, tag):
        """
        특정 태그에 대한 사용자의 카운터만 업데이트
        """

        # 해당 태그에 대한 북마크/북마킹 카운트 계산 (북마크가 있는 경우와 없는 경우 모두 고려)
        tag_data = (
            Tag.objects.filter(pk=tag.pk, meme__bookmarkings__user=user)
            .annotate(
                bc=Count(
                    "meme__bookmarkings",
                    filter=Q(meme__bookmarkings__user=user),
                ),
                bkc=Count(
                    "meme__bookmarkings__bookmark",
                    filter=Q(
                        meme__bookmarkings__bookmark__isnull=False,
                        meme__bookmarkings__user=user,
                    ),
                ),
            )
            .first()
        )

        if tag_data:
            # 카운터가 존재하는 경우 업데이트
            counter, created = cls.objects.get_or_create(
                user=user,
                tag=tag,
                defaults={
                    "bookmarkings_count": tag_data.bc,
                    "bookmarks_count": tag_data.bkc,
                },
            )

            if not created:
                counter.bookmarkings_count = tag_data.bc
                counter.bookmarks_count = tag_data.bkc
                counter.save()

            return counter
        else:
            # 해당 태그에 대한 데이터가 없는 경우 카운터 삭제
            cls.objects.filter(user=user, tag=tag).delete()
            return None
