from config.models import BaseModelWithSoftDelete, SoftDeleteManager
from django.db import models
from django.db.models import QuerySet
from tag.utils.text_splitter import TextSplitter


class TagQuerySet(QuerySet):
    def preparing(self):
        return self.active().filter(published_at__isnull=True)

    def published(self):
        return self.active().filter(published_at__isnull=False)

    def active(self):
        return self.filter(archived_at__isnull=True)

    def archived(self):
        return self.filter(archived_at__isnull=False)


class TagModelManager(SoftDeleteManager.from_queryset(TagQuerySet)):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().all()


class Tag(BaseModelWithSoftDelete):
    class Meta:
        db_table = "tags"
        verbose_name = "tag"
        verbose_name_plural = "tags"

    objects = TagModelManager()

    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    split_name = models.CharField(max_length=1000, null=False, blank=False, default="")
    first_letter = models.CharField(
        max_length=1, null=False, blank=False, default="", db_index=True
    )
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        "tag.TagCategory",
        on_delete=models.CASCADE,
        related_name="tags",
    )

    memes = models.ManyToManyField(
        "meme.Meme",
        through="tag.MemeTagging",
        related_name="tag",
    )

    published_at = models.DateTimeField(
        verbose_name="published at",
        null=True,
        blank=True,
    )

    archived_at = models.DateTimeField(
        verbose_name="archived at",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.split_name = "".join(TextSplitter(self.name).split())
        self.first_letter = self.split_name[0].upper()
        super().save(*args, **kwargs)
