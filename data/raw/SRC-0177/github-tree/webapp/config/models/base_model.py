from django.db import models
from psqlextra.manager import PostgresManager, PostgresQuerySet


class BaseModelQuerySet(PostgresQuerySet):
    pass


class BaseModelManager(PostgresManager.from_queryset(BaseModelQuerySet)):
    pass


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()

    class Meta:
        abstract = True
