from django.apps import apps
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


class TemporaryModelMixin:
  """Utility mixin to register and clean up temporary models for tests."""

  temp_app_label = "users"
  temp_table_prefix = "tmp_common_tests"

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls._temporary_models = []
    cls.setup_models()

  @classmethod
  def tearDownClass(cls):
    try:
      for model in reversed(getattr(cls, "_temporary_models", [])):
        try:
          with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(model)
        except (ProgrammingError, OperationalError):
          if connection.in_atomic_block:
            connection.rollback()
        cls._unregister_model(model._meta.app_label, model._meta.model_name)
      apps.clear_cache()
    finally:
      super().tearDownClass()

  @classmethod
  def setup_models(cls):
    """Hook for subclasses to create temporary models."""

  @classmethod
  def make_model(cls, name, base, fields=None, meta_options=None):
    fields = fields or {}
    attrs = {"__module__": cls.__module__, **fields}
    meta_attrs = {
      "app_label": cls.temp_app_label,
      "db_table": f"{cls.temp_table_prefix}_{name.lower()}",
      "abstract": False,
    }
    if meta_options:
      meta_attrs.update(meta_options)
    base_meta = getattr(base, "Meta", object)
    attrs["Meta"] = type("Meta", (base_meta, ), meta_attrs)
    model = type(name, (base, ), attrs)
    cls._unregister_model(model._meta.app_label, model._meta.model_name)
    apps.register_model(cls.temp_app_label, model)
    apps.clear_cache()
    with connection.schema_editor() as schema_editor:
      schema_editor.create_model(model)
    cls._temporary_models.append(model)
    return model

  @staticmethod
  def _unregister_model(app_label, model_name):
    app_models = apps.all_models.get(app_label, {})
    if model_name in app_models:
      app_models.pop(model_name, None)
