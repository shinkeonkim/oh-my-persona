"""
Financial Statement Item Mapping Rule Model

재무제표 항목 매핑 규칙 모델입니다.
특정 회사 또는 전체 대상으로 계정과목을 매핑하는 규칙을 저장합니다.
"""
from django.db import models

from common.models import BaseModel


class FinancialStatementItemMappingRule(BaseModel):
  """재무제표 항목 매핑 규칙

  특정 account_name/account_id를 다른 account_name/account_id로 매핑하는 규칙입니다.

  예시:
  - 특정 회사의 "단기차입금" → "단기대여금"
  - 전체 회사의 "-표준계정코드 미사용-" → "ifrs_CashAndCashEquivalents"
"""

  class Meta:
    db_table = "financial_statement_item_mapping_rules"
    verbose_name = "재무제표 항목 매핑 규칙"
    verbose_name_plural = "재무제표 항목 매핑 규칙"
    ordering = ["-priority", "company", "source_account_id"]
    indexes = [
      models.Index(fields=["company"], name="idx_fsimr_company"),
      models.Index(fields=["source_account_id"], name="idx_fsimr_src_id"),
      models.Index(fields=["source_account_name"], name="idx_fsimr_src_name"),
      models.Index(fields=["is_active"], name="idx_fsimr_active"),
      models.Index(fields=["-priority"], name="idx_fsimr_priority"),
    ]

  # 대상 회사 (null이면 전체 회사에 적용)
  company = models.ForeignKey(
    "companies.Company",
    on_delete=models.CASCADE,
    related_name="financial_statement_mapping_rules",
    null=True,
    blank=True,
    verbose_name="대상 회사",
    help_text="null이면 전체 회사에 적용됩니다",
  )

  # Source (변환 전)
  source_account_id = models.CharField(
    max_length=255,
    verbose_name="원본 계정과목 ID",
    help_text="변환 전 계정과목 ID (예: ifrs-full_CurrentAssets 또는 -표준계정코드 미사용-)",
  )
  source_account_name = models.CharField(
    max_length=255,
    verbose_name="원본 계정과목명",
    help_text="변환 전 계정과목명 (예: 유동자산)",
  )

  # Target (변환 후)
  target_account_id = models.CharField(
    max_length=255,
    verbose_name="대상 계정과목 ID",
    help_text="변환 후 계정과목 ID (예: ifrs_CurrentAssets)",
  )
  target_account_name = models.CharField(
    max_length=255,
    verbose_name="대상 계정과목명",
    help_text="변환 후 계정과목명 (예: 유동자산)",
  )

  # 메타 정보
  priority = models.IntegerField(
    default=0,
    verbose_name="우선순위",
    help_text="숫자가 높을수록 우선 적용됩니다 (회사별 규칙이 전체 규칙보다 우선)",
  )
  is_active = models.BooleanField(
    default=True,
    verbose_name="활성화 여부",
  )
  description = models.TextField(
    blank=True,
    default="",
    verbose_name="설명",
  )

  def __str__(self) -> str:
    company_str = f"[{self.company.name}]" if self.company else "[전체]"
    return f"{company_str} {self.source_account_name} ({self.source_account_id}) → {self.target_account_name} ({self.target_account_id})"
