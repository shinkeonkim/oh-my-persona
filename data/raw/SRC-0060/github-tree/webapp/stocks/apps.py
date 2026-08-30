from django.apps import AppConfig


class StocksConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'stocks'

  def ready(self):
    """앱이 준비되었을 때 시그널 등록"""
    import stocks.signals  # noqa: F401
