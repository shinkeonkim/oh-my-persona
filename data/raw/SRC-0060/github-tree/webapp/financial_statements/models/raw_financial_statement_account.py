"""
Raw Financial Statement Account Model

원본 재무제표 계정과목 데이터를 저장하는 모델입니다.
"""
from django.db import models

from common.models import BaseModel


class RawFinancialStatementAccount(BaseModel):
  """원본 재무제표 계정과목 모델

  DART API에서 수집한 재무제표 계정과목 원본 데이터를 저장합니다.
  예: 유동자산, 매출채권, 당기순이익 등

  이 데이터는 FinancialStatementItemMappingRule을 통해 정제된 후
  FinancialStatementAccount로 변환됩니다.
  """

  class Meta:
    db_table = "raw_financial_statement_accounts"
    verbose_name = "원본 재무제표 계정과목"
    verbose_name_plural = "원본 재무제표 계정과목"
    indexes = [
      models.Index(fields=["account_id"], name="idx_raw_fsa_account_id"),
      models.Index(fields=["account_name"], name="idx_raw_fsa_account_name"),
    ]
    constraints = [models.UniqueConstraint(
      fields=["account_id", "account_name"],
      name="unique_raw_account_id_name",
    )]

  # 계정과목 정보
  account_id = models.CharField(
    max_length=255,
    verbose_name="계정과목 ID",
    help_text="DART API에서 제공하는 표준계정코드 (예: ifrs_CurrentAssets)",
  )
  account_name = models.CharField(
    max_length=255,
    db_index=True,
    verbose_name="계정과목명",
    help_text="계정과목 이름 (예: 유동자산, 매출채권)",
  )

  # 분류 정보
  account_category = models.CharField(
    max_length=32,
    blank=True,
    default="",
    verbose_name="계정과목 분류",
    help_text="BS(재무상태표), IS(손익계산서), CIS(포괄손익계산서), CF(현금흐름표), SCE(자본변동표)",
  )
  category_name = models.CharField(
    max_length=255,
    blank=True,
    default="",
    verbose_name="재무제표 구분명",
    help_text="sj_nm (예: 재무상태표, 손익계산서)",
  )
  account_detail = models.CharField(
    max_length=255,
    blank=True,
    default="",
    verbose_name="계정과목 상세",
    help_text="account_detail",
  )

  def __str__(self) -> str:
    if self.account_id and self.account_id != "-표준계정코드 미사용-":
      return f"[RAW] {self.account_name} ({self.account_id})"
    return f"[RAW] {self.account_name}"
