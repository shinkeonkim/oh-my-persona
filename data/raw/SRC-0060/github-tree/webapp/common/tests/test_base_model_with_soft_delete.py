from django.db import models
from django.test import TestCase

from common.models.base_model import BaseModelManager
from common.models.base_model_with_soft_delete import (
  BaseModelWithSoftDelete,
  SoftDeleteManager,
  SoftDeleteQuerySet,
)

from .test_utils import TemporaryModelMixin


class BaseModelWithSoftDeleteTests(TemporaryModelMixin, TestCase):
  SoftDeleteAllManager = BaseModelManager.from_queryset(SoftDeleteQuerySet)

  @classmethod
  def setup_models(cls):
    cls.Model = cls.make_model(
      "SoftDeleteConcrete",
      BaseModelWithSoftDelete,
      fields={
        "name": models.CharField(max_length=50),
        "all_objects": cls.SoftDeleteAllManager(),
      },
    )

  def test_default_manager_uses_soft_delete_manager(self):
    self.assertIsInstance(self.Model.objects, SoftDeleteManager)

  def test_soft_delete_marks_deleted_timestamp(self):
    instance = self.Model.objects.create(name="to-delete")
    deleted_count = self.Model.objects.filter(pk=instance.pk).delete()
    self.assertEqual(deleted_count, 1)
    self.assertEqual(self.Model.objects.count(), 0)
    deleted_instance = self.Model.all_objects.get(pk=instance.pk)
    self.assertIsNotNone(deleted_instance.deleted_at)

  def test_restore_unsets_deleted_timestamp(self):
    instance = self.Model.objects.create(name="to-restore")
    self.Model.objects.filter(pk=instance.pk).delete()
    self.Model.all_objects.filter(pk=instance.pk).restore()
    restored = self.Model.objects.get(pk=instance.pk)
    self.assertIsNone(restored.deleted_at)

  def test_hard_delete_removes_row(self):
    instance = self.Model.objects.create(name="to-hard-delete")
    self.Model.objects.filter(pk=instance.pk).delete()
    self.Model.all_objects.filter(pk=instance.pk).hard_delete()
    with self.assertRaises(self.Model.DoesNotExist):
      self.Model.all_objects.get(pk=instance.pk)

  def test_deleted_queryset_returns_only_soft_deleted(self):
    active = self.Model.objects.create(name="active")
    to_delete = self.Model.objects.create(name="deleted")
    self.Model.objects.filter(pk=to_delete.pk).delete()
    deleted_ids = list(self.Model.all_objects.deleted().values_list("pk", flat=True))
    self.assertEqual(deleted_ids, [to_delete.pk])
    self.assertNotIn(active.pk, deleted_ids)
