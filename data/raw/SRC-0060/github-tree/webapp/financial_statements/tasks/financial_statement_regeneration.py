"""
Financial Statement Regeneration Task

Raw 데이터로부터 정제된 재무제표 데이터를 재생성하는 Task입니다.
"""
from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from financial_statements.models import FinancialStatement
from financial_statements.services.financial_statement_regeneration_service import (
  FinancialStatementRegenerationService,
)

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.models import Company

logger = logging.getLogger(__name__)


class RegenerateFinancialStatementsTask(BaseDataIngestTask):
  """재무제표 재생성 Task

  Raw 데이터를 기반으로 Mapping Rule을 적용하여
  정제된 FinancialStatementItem과 FinancialStatementAccount를 생성합니다.

  Raw 데이터는 삭제되지 않고 유지됩니다.
  """

  name = "financial_statements.tasks.regenerate_financial_statements"

  def run(
    self,
    company_id: Optional[int] = None,
    statement_id: Optional[int] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
  ) -> dict:
    """재무제표 재생성 태스크

    Args:
        company_id: 회사 ID (선택)
        statement_id: 재무제표 ID (선택, 지정 시 해당 재무제표만 재생성)
        year: 회계연도 (선택, company_id와 함께 사용)
        quarter: 분기 (선택, company_id와 함께 사용)

    Returns:
        재생성 결과
        {
          "statements_processed": int,
          "total_items_created": int,
          "total_accounts_created": int,
        }
    """
    service = FinancialStatementRegenerationService()

    # 1. 특정 재무제표만 재생성
    if statement_id:
      try:
        statement = FinancialStatement.objects.get(pk=statement_id)
        result = service.regenerate_for_statement(statement)
        logger.info(
          "Regenerated single statement: statement_id=%s items_created=%s accounts_created=%s",
          statement_id,
          result.get("items_created", 0),
          result.get("accounts_created", 0),
        )
        return {
          "statements_processed": 1,
          "total_items_created": result.get("items_created", 0),
          "total_accounts_created": result.get("accounts_created", 0),
        }
      except FinancialStatement.DoesNotExist:
        logger.error("Statement not found: statement_id=%s", statement_id)
        return {
          "statements_processed": 0,
          "total_items_created": 0,
          "total_accounts_created": 0,
          "error": f"Statement {statement_id} not found",
        }

    # 2. 회사별 재생성
    if company_id:
      try:
        company = Company.objects.get(pk=company_id)
        result = service.regenerate_for_company(company, year=year, quarter=quarter)
        logger.info(
          "Regenerated statements for company: company_id=%s year=%s quarter=%s "
          "statements_processed=%s items_created=%s accounts_created=%s",
          company_id,
          year,
          quarter,
          result.get("statements_processed", 0),
          result.get("total_items_created", 0),
          result.get("total_accounts_created", 0),
        )
        return result
      except Company.DoesNotExist:
        logger.error("Company not found: company_id=%s", company_id)
        return {
          "statements_processed": 0,
          "total_items_created": 0,
          "total_accounts_created": 0,
          "error": f"Company {company_id} not found",
        }

    # 3. 전체 재생성 (매우 위험 - 사용 주의)
    logger.warning("Regenerating ALL financial statements - this may take a very long time")

    statements = FinancialStatement.objects.all()
    if year:
      statements = statements.filter(fiscal_year=year)
    if quarter:
      statements = statements.filter(fiscal_quarter=quarter)

    statements_processed = 0
    total_items_created = 0
    total_accounts_created = 0

    for statement in statements:
      try:
        result = service.regenerate_for_statement(statement)
        statements_processed += 1
        total_items_created += result.get("items_created", 0)
        total_accounts_created += result.get("accounts_created", 0)

        if statements_processed % 10 == 0:
          logger.info(
            "Regeneration progress: %s statements processed",
            statements_processed,
          )
      except Exception as exc:
        logger.exception(
          "Failed to regenerate statement: statement_id=%s error=%s",
          statement.id,
          exc,
        )

    logger.info(
      "Regeneration completed: statements_processed=%s items_created=%s accounts_created=%s",
      statements_processed,
      total_items_created,
      total_accounts_created,
    )

    return {
      "statements_processed": statements_processed,
      "total_items_created": total_items_created,
      "total_accounts_created": total_accounts_created,
    }


# Celery task 인스턴스 생성
regenerate_financial_statements = shared_task(
  base=RegenerateFinancialStatementsTask,
  bind=True,
)(RegenerateFinancialStatementsTask().run)
