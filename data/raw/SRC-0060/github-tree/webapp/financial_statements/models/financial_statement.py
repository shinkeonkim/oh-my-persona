from django.db import models

from common.models import BaseModel


class FinancialStatement(BaseModel):

  class Meta:
    db_table = "financial_statements"
    verbose_name = "재무제표"
    verbose_name_plural = "재무제표"
    constraints = [
      models.UniqueConstraint(
        fields=["company", "fiscal_year", "fiscal_quarter", "report_type", "source"],
        name="unique_company_year_quarter_report_source",
      )
    ]
    indexes = [
      models.Index(fields=["company", "-fiscal_year", "-fiscal_quarter"], name="idx_fs_company_period"),
      models.Index(fields=["company", "source"], name="idx_fs_company_source"),
    ]

  REPORT_TYPE_CHOICES = (
    ("q1", "1분기보고서"),
    ("half", "반기보고서"),
    ("q3", "3분기보고서"),
    ("annual", "사업보고서"),
  )

  SOURCE_CHOICES = (
    ("CFS", "연결재무제표"),
    ("OFS", "재무제표(개별)"),
  )

  company = models.ForeignKey(
    "companies.Company",
    on_delete=models.CASCADE,
    related_name="financial_statements",
  )

  fiscal_year = models.PositiveIntegerField()
  fiscal_quarter = models.PositiveSmallIntegerField()
  report_type = models.CharField(max_length=16, choices=REPORT_TYPE_CHOICES)
  currency = models.CharField(max_length=10, default="KRW")
  is_consolidated = models.BooleanField(default=True)
  submission_date = models.DateField(null=True, blank=True)
  receipt_no = models.CharField(max_length=20, blank=True)
  source = models.CharField(max_length=3, choices=SOURCE_CHOICES, blank=True)

  def __str__(self) -> str:
    return f"{self.company.name} {self.fiscal_year} Q{self.fiscal_quarter}"
