from django.db import models


class GenerationStatusChoice(models.TextChoices):
  PENDING = "PENDING", "초기화됨"
  GENERATING = "GENERATING", "생성 중"
  COMPLETED = "COMPLETED", "생성완료"
  FAILED = "FAILED", "생성실패"
