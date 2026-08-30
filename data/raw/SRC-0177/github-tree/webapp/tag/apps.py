from django.apps import AppConfig


class TagConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tag"

    def ready(self):
        # 시그널 등록
        import tag.signals  # noqa
