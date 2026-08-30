from django.db import models

from common.models import BaseModel


class CompanyDisclosure(BaseModel):
  """
  회사 공시 정보를 저장하는 모델입니다.
  """

  class Meta:
    db_table = "company_disclosures"
    verbose_name = "Company Disclosure"
    verbose_name_plural = "Company Disclosures"
    indexes = [
      models.Index(fields=["company", "-published_at"]),
      models.Index(fields=["receipt_no"]),
    ]
    constraints = [
      models.UniqueConstraint(fields=["company", "receipt_no"], name="unique_company_receipt_no"),
    ]

  company = models.ForeignKey(
    "companies.Company",
    on_delete=models.CASCADE,
    related_name="disclosures",
  )
  receipt_no = models.CharField(max_length=30)
  title = models.CharField(max_length=500)
  published_at = models.DateTimeField()
  text_body = models.TextField(blank=True)
  html_body = models.TextField(blank=True)
  disclosure_type = models.CharField(max_length=100, blank=True)
  source_url = models.URLField(max_length=500, blank=True)

  def __str__(self) -> str:
    return f"{self.company.name} - {self.title}"
