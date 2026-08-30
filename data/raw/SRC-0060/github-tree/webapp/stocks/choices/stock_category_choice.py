from django.db import models


class StockCategoryChoice(models.TextChoices):
  COMMON = "common", "보통주"
  PREFERRED = "preferred", "우선주"
  # 구형 우선주
  OLD_PREFERRED = "old_preferred", "구형 우선주"
  # 신형 우선주
  NEW_PREFERRED = "new_preferred", "신형 우선주"
  OTHER = "other", "기타"
