from django.db import models


class ProfileStatusChoices(models.TextChoices):
    INACTIVE = "inactive", "비활성"
    PENDING = "pending", "승인 대기"
    ACTIVE = "active", "승인 완료"
