from django.db import models

from common.models import BaseModel


class Country(BaseModel):
  """국가 모델"""

  class Meta:
    db_table = "countries"
    verbose_name = "Country"
    verbose_name_plural = "Countries"

  code = models.CharField(
    max_length=10,
    unique=True,
    verbose_name="국가 코드",
  )
  name = models.CharField(max_length=100, verbose_name="국가명")

  def __str__(self) -> str:
    return f"{self.name} ({self.code})"
