from django.db import models

from common.models import BaseModel

from .financial_statement import FinancialStatement


class FinancialStatementItem(BaseModel):

  class Meta:
    db_table = "financial_statement_items"
    verbose_name = "재무제표 항목"
    verbose_name_plural = "재무제표 항목"
    constraints = [models.UniqueConstraint(
      fields=["statement", "account"],
      name="unique_statement_account",
    )]
    indexes = [
      models.Index(fields=["statement", "account"], name="idx_fsi_statement_account"),
    ]

  statement = models.ForeignKey(
    FinancialStatement,
    on_delete=models.CASCADE,
    related_name="items",
    verbose_name="재무제표",
  )
  account = models.ForeignKey(
    "financial_statements.FinancialStatementAccount",
    on_delete=models.PROTECT,
    related_name="items",
    verbose_name="계정과목",
  )

  # 금액 데이터
  current_amount = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="당기금액",
    help_text="thstrm_amount",
  )
  cumulative_amount = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="당기누적금액",
    help_text="thstrm_add_amount",
  )

  # 메타데이터
  order = models.IntegerField(default=0, verbose_name="정렬순서")
  raw = models.JSONField(default=dict, blank=True, verbose_name="원본 데이터")

  def __str__(self) -> str:
    return f"{self.statement_id} - {self.account.account_name}"
