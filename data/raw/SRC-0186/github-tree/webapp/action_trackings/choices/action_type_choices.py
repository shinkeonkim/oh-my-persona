from django.db import models


class ActionTypeChoices(models.TextChoices):
  """액션 타입 선택지"""

  # 프로필 관련
  PROFILE_VIEW = "profile_view", "프로필 조회"
