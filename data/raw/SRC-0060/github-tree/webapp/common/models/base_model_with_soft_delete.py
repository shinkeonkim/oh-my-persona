from django.db import models

from .base_model import BaseModel, BaseModelManager, BaseModelQuerySet


class SoftDeleteQuerySet(BaseModelQuerySet):

  def delete(self):
    return super().update(deleted_at=models.functions.Now())

  def hard_delete(self):
    return super().delete()

  def active(self):
    return self.filter(deleted_at__isnull=True)

  def deleted(self):
    return self.filter(deleted_at__isnull=False)

  def with_deleted(self):
    return self.all()

  def restore(self):
    return super().update(deleted_at=None)


class SoftDeleteManager(BaseModelManager.from_queryset(SoftDeleteQuerySet)):

  def get_queryset(self):
    return super().get_queryset().active()


class BaseModelWithSoftDelete(BaseModel):

  class Meta:
    abstract = True
    verbose_name = "Base Model with Soft Delete"
    verbose_name_plural = "Base Models with Soft Delete"

  objects = SoftDeleteManager()

  deleted_at = models.DateTimeField(null=True, blank=True)
