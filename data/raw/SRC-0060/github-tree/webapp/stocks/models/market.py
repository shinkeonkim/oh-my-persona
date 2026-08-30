from django.db import models

from stocks.choices import MarketCodeChoice

from common.models import BaseModel


class Market(BaseModel):
  """주식 시장 모델"""

  class Meta:
    db_table = "markets"
    verbose_name = "Market"
    verbose_name_plural = "Markets"

  name = models.CharField(max_length=255, verbose_name="시장명")
  code = models.CharField(
    max_length=50,
    choices=MarketCodeChoice.choices,
    unique=True,
    verbose_name="시장 코드",
  )
  country = models.ForeignKey(
    "companies.Country",
    on_delete=models.PROTECT,
    related_name="markets",
    verbose_name="국가",
  )

  def __str__(self) -> str:
    return f"{self.name} ({self.code})"
