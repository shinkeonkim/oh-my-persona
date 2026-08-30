from django.apps import AppConfig


class MatchmakingsConfig(AppConfig):
  default_auto_field = "django.db.models.BigAutoField"
  name = "matchmakings"

  def ready(self):
    import matchmakings.signals  # noqa
