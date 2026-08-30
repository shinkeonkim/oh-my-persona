"""
Raw Financial Statement Item Model

원본 재무제표 항목 데이터를 저장하는 모델입니다.
DART API에서 받은 데이터를 변환 없이 그대로 저장합니다.
"""
from django.db import models

from common.models import BaseModel


class RawFinancialStatementItem(BaseModel):
  """원본 재무제표 항목

  DART API에서 수집한 재무제표 항목 원본 데이터를 저장합니다.
  이 데이터는 FinancialStatementItemMappingRule을 통해 정제된 후
  FinancialStatementItem으로 변환됩니다.
  """

  class Meta:
    db_table = "raw_financial_statement_items"
    verbose_name = "원본 재무제표 항목"
    verbose_name_plural = "원본 재무제표 항목"
    constraints = [models.UniqueConstraint(
      fields=["statement", "account"],
      name="unique_raw_statement_account",
    )]
    indexes = [
      models.Index(fields=["statement"], name="idx_raw_fsi_statement"),
      models.Index(fields=["account"], name="idx_raw_fsi_account"),
    ]

  statement = models.ForeignKey(
    "financial_statements.FinancialStatement",
    on_delete=models.CASCADE,
    related_name="raw_items",
    verbose_name="재무제표",
  )
  account = models.ForeignKey(
    "financial_statements.RawFinancialStatementAccount",
    on_delete=models.PROTECT,
    related_name="raw_items",
    verbose_name="원본 계정과목",
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
    return f"[RAW] {self.statement_id} - {self.account.account_name}"
