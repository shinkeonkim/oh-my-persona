from __future__ import annotations

import logging
from typing import Iterable

from celery import shared_task
from financial_statements.services.financial_statement_service import FinancialStatementService

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.models import Company

logger = logging.getLogger(__name__)


class IngestFinancialStatementsTask(BaseDataIngestTask):
  """재무제표 수집 Task (Raw 데이터만 저장)"""

  name = "companies.tasks.ingest_financial_statements"

  def run(
    self,
    company_id: int,
    years: Iterable[int],
    quarters: Iterable[int],
    page_count: int = 100,
  ) -> dict:
    """재무제표 수집 태스크 (CFS와 OFS 모두 수집)

    Raw 데이터만 저장합니다.
    정제된 데이터를 생성하려면 regenerate_financial_statements task를 별도로 실행하세요.

    Args:
        company_id: 회사 ID
        years: 회계연도 리스트
        quarters: 분기 리스트 (1, 2, 3, 4)
        page_count: 페이지당 항목 수

    Returns:
        수집 결과 딕셔너리
        {
          "company_id": int,
          "statements": [
            {"year": 2024, "quarter": 4, "CFS": statement_id, "OFS": statement_id},
            ...
          ]
        }
    """
    company = Company.objects.filter(pk=company_id).first()
    if not company:
      logger.warning("Company %s not found while ingesting financial statements", company_id)
      return {"company_id": company_id, "statements": []}

    if not company.corp_code:
      logger.warning("Company %s has no corp_code; skipping financial statement ingest", company_id)
      return {"company_id": company_id, "statements": []}

    service = FinancialStatementService()
    statements = []

    for year in years:
      for quarter in quarters:
        try:
          # Raw 데이터 수집
          result = service.perform(company, int(year), int(quarter), page_count=page_count)
          if result:
            statements.append({
              "year": year,
              "quarter": quarter,
              **result,  # CFS, OFS 키를 포함
            })
            logger.info(
              "Successfully ingested raw financial statements company_id=%s year=%s quarter=%s result=%s",
              company_id,
              year,
              quarter,
              result,
            )
        except Exception as exc:  # pylint: disable=broad-except
          logger.exception(
            "Failed to ingest financial statement company_id=%s year=%s quarter=%s error=%s",
            company_id,
            year,
            quarter,
            exc,
          )

    logger.info(
      "Financial statement ingest task completed company_id=%s total_statements=%s",
      company_id,
      len(statements),
    )

    return {"company_id": company_id, "statements": statements}


# Celery task 인스턴스 생성
ingest_financial_statements = shared_task(base=IngestFinancialStatementsTask,
                                          bind=True)(IngestFinancialStatementsTask().run)
