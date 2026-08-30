from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

from django.db import transaction

from financial_statements.models import (
  FinancialStatement,
  RawFinancialStatementAccount,
  RawFinancialStatementItem,
)

from common.clients.dart import (
  FinancialStatementDartClient,
)
from companies.models import (
  Company,
)

logger = logging.getLogger(__name__)

QUARTER_TO_REPORT_TYPE = {1: "q1", 2: "half", 3: "q3", 4: "annual"}


class FinancialStatementService:

  def __init__(self, client: Optional[FinancialStatementDartClient] = None) -> None:
    """초기화

        Args:
            client: FinancialStatementDartClient 인스턴스 (None이면 새로 생성)
        """
    self.client = client or FinancialStatementDartClient()

  def perform(self, company: Company, year: int, quarter: int, page_count: int = 100) -> Dict[str, int]:
    """재무제표 데이터 수집 (CFS와 OFS 모두 수집)

    Args:
        company: 대상 회사
        year: 회계연도
        quarter: 분기 (1, 2, 3, 4)
        page_count: 페이지당 항목 수

    Returns:
        수집된 재무제표 ID 딕셔너리 {"CFS": statement_id, "OFS": statement_id}
    """
    report_type = QUARTER_TO_REPORT_TYPE.get(quarter, "annual")

    logger.info(
      "Starting financial statement ingest company_id=%s corp_code=%s year=%s quarter=%s",
      company.id,
      company.corp_code,
      year,
      quarter,
    )

    result = {}

    # CFS (연결재무제표) 수집
    cfs_payload, success = self.client.fetch_financial_statement(
      corp_code=company.corp_code,
      year=year,
      quarter=quarter,
      fs_div="CFS",
      page_count=page_count,
    )
    if success and cfs_payload:
      statement_id = self._create_or_update_statement(
        company=company,
        year=year,
        quarter=quarter,
        report_type=report_type,
        source="CFS",
        is_consolidated=True,
        payload=cfs_payload,
      )
      if statement_id:
        result["CFS"] = statement_id
        logger.info("CFS statement created/updated: statement_id=%s", statement_id)

    # OFS (개별재무제표) 수집
    ofs_payload, success = self.client.fetch_financial_statement(
      corp_code=company.corp_code,
      year=year,
      quarter=quarter,
      fs_div="OFS",
      page_count=page_count,
    )
    if success and ofs_payload:
      statement_id = self._create_or_update_statement(
        company=company,
        year=year,
        quarter=quarter,
        report_type=report_type,
        source="OFS",
        is_consolidated=False,
        payload=ofs_payload,
      )
      if statement_id:
        result["OFS"] = statement_id
        logger.info("OFS statement created/updated: statement_id=%s", statement_id)

    if not result:
      logger.warning(
        "No financial statement data found for company_id=%s corp_code=%s year=%s quarter=%s",
        company.id,
        company.corp_code,
        year,
        quarter,
      )

    logger.info(
      "Financial statement ingest complete company_id=%s year=%s quarter=%s result=%s",
      company.id,
      year,
      quarter,
      result,
    )
    return result

  def _create_or_update_statement(
    self,
    company: Company,
    year: int,
    quarter: int,
    report_type: str,
    source: str,
    is_consolidated: bool,
    payload: List[Dict[str, str]],
  ) -> Optional[int]:
    """재무제표 생성 또는 업데이트"""
    if not payload:
      return None

    first_item = payload[0]
    receipt_no = first_item.get("rcept_no", "")
    submission_date = self._parse_submission_date(receipt_no)

    with transaction.atomic():
      statement, created = FinancialStatement.objects.update_or_create(
        company=company,
        fiscal_year=year,
        fiscal_quarter=quarter,
        report_type=report_type,
        source=source,
        defaults={
          "is_consolidated": is_consolidated,
          "submission_date": submission_date,
          "currency": first_item.get("currency", "KRW") or "KRW",
          "receipt_no": receipt_no,
        },
      )
      self._upsert_raw_items(statement, payload)

    return statement.id

  def _upsert_raw_items(self, statement: FinancialStatement, rows: List[Dict[str, str]]) -> None:
    """원본 재무제표 항목 생성 또는 업데이트 (Raw 데이터 저장)"""
    for row in rows:
      account_id = (row.get("account_id") or "").strip()
      account_name = (row.get("account_nm") or "").strip()
      account_category = (row.get("sj_div") or "").strip()
      category_name = (row.get("sj_nm") or "").strip()
      account_detail = (row.get("account_detail") or "").strip()

      if not account_name:
        continue

      # 계정과목이 없으면 "-표준계정코드 미사용-"으로 저장
      if not account_id:
        account_id = "-표준계정코드 미사용-"

      # RawFinancialStatementAccount 가져오기 또는 생성
      raw_account, _ = RawFinancialStatementAccount.objects.get_or_create(
        account_id=account_id,
        account_name=account_name,
        defaults={
          "account_category": account_category,
          "category_name": category_name,
          "account_detail": account_detail,
        },
      )

      # RawFinancialStatementItem 생성 또는 업데이트
      RawFinancialStatementItem.objects.update_or_create(
        statement=statement,
        account=raw_account,
        defaults={
          "current_amount": self._to_decimal(row.get("thstrm_amount")),
          "cumulative_amount": self._to_decimal(row.get("thstrm_add_amount")),
          "order": self._to_int(row.get("ord")),
          "raw": row,
        },
      )

  @staticmethod
  def _parse_submission_date(receipt_no: str) -> Optional[datetime.date]:
    if not receipt_no or len(receipt_no) < 8:
      return None
    try:
      naive = datetime.strptime(receipt_no[:8], "%Y%m%d")
      return naive.date()
    except ValueError:
      return None

  @staticmethod
  def _to_decimal(value: Optional[str]) -> Optional[Decimal]:
    if value in (None, "", "-", "NaN"):
      return None
    cleaned = str(value).replace(",", "").strip()
    try:
      return Decimal(cleaned)
    except (InvalidOperation, ValueError):
      logger.debug("Unable to convert value '%s' to Decimal", value)
      return None

  @staticmethod
  def _to_int(value: Optional[str]) -> int:
    """문자열을 정수로 변환"""
    if value in (None, "", "-"):
      return 0
    try:
      return int(value)
    except (ValueError, TypeError):
      logger.debug("Unable to convert value '%s' to int", value)
      return 0
