from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        pass  # 현재는 시그널이 없지만, 필요할 경우를 대비해 ready 메서드 추가
