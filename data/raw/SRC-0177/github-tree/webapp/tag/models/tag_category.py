from config.models import BaseModelWithSoftDelete
from django.db import models


class TagCategory(BaseModelWithSoftDelete):
    class Meta:
        db_table = "tag_categories"
        verbose_name = "tag_category"
        verbose_name_plural = "tag_categories"

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
