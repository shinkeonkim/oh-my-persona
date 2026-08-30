from django.apps import AppConfig


class FileManagersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "file_managers"

    def ready(self):
        import file_managers.signals  # noqa
