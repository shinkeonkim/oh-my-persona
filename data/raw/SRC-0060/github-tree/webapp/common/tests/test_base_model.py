from django.db import models
from django.test import TestCase

from common.models.base_model import BaseModel, BaseModelManager, BaseModelQuerySet

from .test_utils import TemporaryModelMixin


class BaseModelTests(TemporaryModelMixin, TestCase):

  @classmethod
  def setup_models(cls):
    cls.Model = cls.make_model(
      "BaseModelConcrete",
      BaseModel,
      fields={
        "name": models.CharField(max_length=50),
      },
    )

  def test_meta_configuration(self):
    meta = self.Model._meta
    print(meta.__dict__)
    self.assertEqual(meta.ordering, ["-created_at"])
    self.assertEqual(meta.get_latest_by, "created_at")
    self.assertEqual(meta.verbose_name, "Base Model")
    self.assertEqual(meta.verbose_name_plural, "Base Models")
    self.assertEqual(
      {tuple(index.fields)
       for index in meta.indexes},
      {("-created_at", ), ("-updated_at", )},
    )

  def test_default_manager_and_queryset(self):
    self.assertIsInstance(self.Model.objects, BaseModelManager)
    queryset = self.Model.objects.all()
    self.assertIsInstance(queryset, BaseModelQuerySet)

  def test_timestamp_fields_populated(self):
    instance = self.Model.objects.create(name="example")
    self.assertIsNotNone(instance.created_at)
    self.assertIsNotNone(instance.updated_at)
    self.assertLessEqual(instance.created_at, instance.updated_at)

  def test_ordering_returns_latest_first(self):
    self.Model.objects.create(name="first")
    second = self.Model.objects.create(name="second")
    latest = self.Model.objects.first()
    self.assertEqual(latest, second)
    ordered_names = list(self.Model.objects.values_list("name", flat=True))
    self.assertEqual(ordered_names, ["second", "first"])
