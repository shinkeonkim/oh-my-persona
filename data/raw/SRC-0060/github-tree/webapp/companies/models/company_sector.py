from django.db import models

from common.models import BaseModel


class CompanySector(BaseModel):

  class Meta:
    db_table = "company_sectors"
    verbose_name = "Company Sector"
    verbose_name_plural = "Company Sectors"
    ordering = ["name"]

  name = models.CharField(max_length=100, unique=True)

  def __str__(self) -> str:
    return self.name
