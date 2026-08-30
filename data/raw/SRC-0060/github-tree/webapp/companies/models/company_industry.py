from django.db import models

from common.models import BaseModel


class CompanyIndustry(BaseModel):

  class Meta:
    db_table = "company_industries"
    verbose_name = "Company Industry"
    verbose_name_plural = "Company Industries"
    ordering = ["name"]

  name = models.CharField(max_length=100, unique=True)

  def __str__(self) -> str:
    return self.name
