"""
Financial Statement Ingest and Regeneration Task

재무제표 수집과 재생성을 한번에 처리하는 통합 Task입니다.
"""
from __future__ import annotations

import logging
from typing import Iterable

from celery import shared_task
from financial_statements.services.financial_statement_regeneration_service import (
  FinancialStatementRegenerationService,
)
from financial_statements.services.financial_statement_service import FinancialStatementService

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.models import Company

logger = logging.getLogger(__name__)


class IngestAndRegenerateFinancialStatementsTask(BaseDataIngestTask):
  """재무제표 수집 및 재생성 통합 Task

  1. Raw 재무제표 데이터 수집 (Ingest)
  2. 수집된 데이터를 기반으로 정제된 재무제표 재생성 (Regeneration)

  두 작업을 순차적으로 실행합니다.
  """

  name = "financial_statements.tasks.ingest_and_regenerate_financial_statements"

  def run(
    self,
    company_id: int,
    years: Iterable[int],
    quarters: Iterable[int],
    page_count: int = 100,
  ) -> dict:
    """재무제표 수집 및 재생성 태스크

    Args:
        company_id: 회사 ID
        years: 회계연도 리스트
        quarters: 분기 리스트 (1, 2, 3, 4)
        page_count: 페이지당 항목 수

    Returns:
        수집 및 재생성 결과 딕셔너리
        {
          "company_id": int,
          "ingest_results": [...],
          "regeneration_results": {
            "statements_processed": int,
            "total_items_created": int,
            "total_accounts_created": int,
          }
        }
    """
    company = Company.objects.filter(pk=company_id).first()
    if not company:
      logger.warning("Company %s not found while ingesting financial statements", company_id)
      return {"company_id": company_id, "ingest_results": [], "regeneration_results": {}, "error": "Company not found"}

    if not company.corp_code:
      logger.warning("Company %s has no corp_code; skipping financial statement ingest", company_id)
      return {"company_id": company_id, "ingest_results": [], "regeneration_results": {}, "error": "No corp_code"}

    # Phase 1: Ingest raw data
    logger.info(
      "Starting Phase 1: Ingest raw financial statements for company_id=%s years=%s quarters=%s",
      company_id,
      years,
      quarters,
    )

    ingest_service = FinancialStatementService()
    ingest_results = []

    for year in years:
      for quarter in quarters:
        try:
          result = ingest_service.perform(company, int(year), int(quarter), page_count=page_count)
          if result:
            ingest_results.append({
              "year": year,
              "quarter": quarter,
              **result,  # CFS, OFS 키 포함
            })
            logger.info(
              "Successfully ingested raw financial statements company_id=%s year=%s quarter=%s result=%s",
              company_id,
              year,
              quarter,
              result,
            )
        except Exception as exc:
          logger.exception(
            "Failed to ingest financial statement company_id=%s year=%s quarter=%s error=%s",
            company_id,
            year,
            quarter,
            exc,
          )

    logger.info(
      "Phase 1 completed: Ingested %s statements for company_id=%s",
      len(ingest_results),
      company_id,
    )

    # Phase 2: Regenerate cleaned data
    logger.info(
      "Starting Phase 2: Regenerate financial statements for company_id=%s years=%s quarters=%s",
      company_id,
      years,
      quarters,
    )

    regeneration_service = FinancialStatementRegenerationService()
    regeneration_results = {
      "statements_processed": 0,
      "total_items_created": 0,
      "total_accounts_created": 0,
    }

    try:
      # 각 연도/분기 조합에 대해 재생성
      for year in years:
        for quarter in quarters:
          result = regeneration_service.regenerate_for_company(company, year=year, quarter=quarter)
          regeneration_results["statements_processed"] += result.get("statements_processed", 0)
          regeneration_results["total_items_created"] += result.get("total_items_created", 0)
          regeneration_results["total_accounts_created"] += result.get("total_accounts_created", 0)

          logger.info(
            "Regenerated statements company_id=%s year=%s quarter=%s "
            "statements_processed=%s items_created=%s accounts_created=%s",
            company_id,
            year,
            quarter,
            result.get("statements_processed", 0),
            result.get("total_items_created", 0),
            result.get("total_accounts_created", 0),
          )

    except Exception as exc:
      logger.exception(
        "Failed to regenerate financial statements company_id=%s error=%s",
        company_id,
        exc,
      )
      regeneration_results["error"] = str(exc)

    logger.info(
      "Phase 2 completed: Regenerated statements for company_id=%s "
      "statements_processed=%s items_created=%s accounts_created=%s",
      company_id,
      regeneration_results["statements_processed"],
      regeneration_results["total_items_created"],
      regeneration_results["total_accounts_created"],
    )

    return {
      "company_id": company_id,
      "ingest_results": ingest_results,
      "regeneration_results": regeneration_results,
    }


# Celery task 인스턴스 생성
ingest_and_regenerate_financial_statements = shared_task(
  base=IngestAndRegenerateFinancialStatementsTask,
  bind=True,
)(IngestAndRegenerateFinancialStatementsTask().run)
