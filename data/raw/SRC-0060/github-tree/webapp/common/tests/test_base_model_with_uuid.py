import uuid

from django.db import models
from django.test import TestCase

from common.models.base_model_with_uuid import BaseModelWithUUID

from .test_utils import TemporaryModelMixin


class BaseModelWithUUIDTests(TemporaryModelMixin, TestCase):

  @classmethod
  def setup_models(cls):
    cls.Model = cls.make_model(
      "UUIDConcreteModel",
      BaseModelWithUUID,
      fields={
        "name": models.CharField(max_length=50),
      },
    )

  def test_uuid_is_primary_key(self):
    instance = self.Model.objects.create(name="uuid-test")
    self.assertIsInstance(instance.pk, uuid.UUID)
    self.assertEqual(instance.pk, instance.uuid)
    self.assertFalse(instance._meta.pk.auto_created)

  def test_uuid_is_immutable_after_update(self):
    instance = self.Model.objects.create(name="immutable-test")
    original_uuid = instance.uuid
    instance.name = "updated"
    instance.save()
    instance.refresh_from_db()
    self.assertEqual(instance.uuid, original_uuid)

  def test_uuid_model_inherits_timestamp_fields(self):
    instance = self.Model.objects.create(name="timestamps")
    self.assertIsNotNone(instance.created_at)
    self.assertIsNotNone(instance.updated_at)
