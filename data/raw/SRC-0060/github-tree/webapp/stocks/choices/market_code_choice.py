from django.db import models


class MarketCodeChoice(models.TextChoices):
  """주식 시장 코드 선택지"""

  KOSPI = "KOSPI", "코스피"
  KOSDAQ = "KOSDAQ", "코스닥"
