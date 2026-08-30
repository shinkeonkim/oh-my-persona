"""
Bulk Financial Statement Ingest and Regeneration Task

모든 회사에 대해 특정 연도의 재무제표를 배치 단위로 수집하고 재생성하는 Task입니다.
API 요청 제한을 고려하여 배치 단위로 나누어 처리하며, 각 배치 사이에 sleep을 추가합니다.
"""
from __future__ import annotations

import logging
import time
from typing import Iterable

from django.db.models import Q

from celery import shared_task

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.models import Company

from .financial_statement_ingest_and_regeneration import ingest_and_regenerate_financial_statements

logger = logging.getLogger(__name__)


class BulkIngestAndRegenerateFinancialStatementsTask(BaseDataIngestTask):
  """전체 회사 재무제표 수집 및 재생성 배치 Task

  API 요청 제한을 고려하여:
  1. 회사 목록을 배치 단위로 나눔
  2. 각 배치를 순차적으로 처리
  3. 배치 사이에 sleep 추가
  4. 각 회사별로는 비동기 Task 실행

  약 3700개 회사 기준:
  - 배치 크기 25개 × 148 배치 = 3700개
  - 배치당 sleep 180초 (3분) × 148 = 444분 (약 7.4시간)
  - 하루 안에 완료 가능
  """

  name = "financial_statements.tasks.bulk_ingest_and_regenerate_financial_statements"

  def run(
    self,
    fiscal_year: int,
    quarters: Iterable[int] = None,
    is_listed_only: bool = False,
    is_financial_excluded: bool = False,
    batch_size: int = 25,
    sleep_seconds: int = 180,
    page_count: int = 100,
  ) -> dict:
    """전체 회사 재무제표 수집 및 재생성 태스크

    Args:
        fiscal_year: 회계연도
        quarters: 분기 리스트 (기본값: [1, 2, 3, 4])
        is_listed_only: 상장 회사만 처리할지 여부
        is_financial_excluded: 금융업 제외 여부
        batch_size: 배치당 회사 수 (기본값: 25)
        sleep_seconds: 배치 사이 대기 시간(초) (기본값: 180초 = 3분)
        page_count: DART API 요청당 페이지 수

    Returns:
        배치 처리 결과 딕셔너리
        {
          "total_companies": int,
          "batches_processed": int,
          "tasks_queued": int,
          "batch_size": int,
          "sleep_seconds": int,
          "estimated_completion_hours": float,
        }
    """
    if quarters is None:
      quarters = [1, 2, 3, 4]

    logger.info(
      "Starting bulk financial statement ingest and regeneration for year=%s quarters=%s "
      "is_listed_only=%s is_financial_excluded=%s batch_size=%s sleep_seconds=%s",
      fiscal_year,
      quarters,
      is_listed_only,
      is_financial_excluded,
      batch_size,
      sleep_seconds,
    )

    # 대상 회사 필터링
    queryset = Company.objects.filter(corp_code__isnull=False).exclude(corp_code="")

    if is_listed_only:
      queryset = queryset.filter(stocks__is_listed=True).distinct()

    if is_financial_excluded:
      queryset = queryset.filter(Q(is_financial=False) | Q(is_financial__isnull=True))

    # 회사 ID 목록 가져오기
    company_ids = list(queryset.values_list('pk', flat=True).order_by('pk'))
    total_companies = len(company_ids)

    logger.info(
      "Found %s companies to process (is_listed_only=%s, is_financial_excluded=%s)",
      total_companies,
      is_listed_only,
      is_financial_excluded,
    )

    if total_companies == 0:
      logger.warning("No companies found to process")
      return {
        "total_companies": 0,
        "batches_processed": 0,
        "tasks_queued": 0,
        "batch_size": batch_size,
        "sleep_seconds": sleep_seconds,
        "estimated_completion_hours": 0,
      }

    # 배치 단위로 나누어 처리
    batches_processed = 0
    tasks_queued = 0
    total_batches = (total_companies + batch_size - 1) // batch_size  # 올림 나눗셈

    logger.info("Processing %s companies in %s batches of size %s", total_companies, total_batches, batch_size)

    for batch_index in range(0, total_companies, batch_size):
      batch_company_ids = company_ids[batch_index:batch_index + batch_size]
      batches_processed += 1

      logger.info(
        "Processing batch %s/%s with %s companies (IDs: %s...%s)",
        batches_processed,
        total_batches,
        len(batch_company_ids),
        batch_company_ids[0] if batch_company_ids else "N/A",
        batch_company_ids[-1] if batch_company_ids else "N/A",
      )

      # 현재 배치의 각 회사에 대해 비동기 Task 실행
      for company_id in batch_company_ids:
        try:
          task = ingest_and_regenerate_financial_statements.delay(
            company_id=company_id,
            years=[fiscal_year],
            quarters=quarters,
            page_count=page_count,
          )
          tasks_queued += 1

          logger.debug("Queued task for company_id=%s task_id=%s", company_id, task.id)

        except Exception as exc:
          logger.exception("Failed to queue task for company_id=%s error=%s", company_id, exc)

      # 마지막 배치가 아니면 sleep
      if batches_processed < total_batches:
        logger.info(
          "Batch %s/%s completed. Queued %s tasks. Sleeping for %s seconds before next batch...",
          batches_processed,
          total_batches,
          len(batch_company_ids),
          sleep_seconds,
        )
        time.sleep(sleep_seconds)
      else:
        logger.info(
          "Final batch %s/%s completed. Queued %s tasks. No sleep needed.", batches_processed, total_batches,
          len(batch_company_ids)
        )

    # 예상 완료 시간 계산 (sleep 시간만 고려, 실제 작업 시간은 Celery Worker에 의존)
    estimated_sleep_hours = (total_batches - 1) * sleep_seconds / 3600

    logger.info(
      "Bulk financial statement ingest and regeneration completed. "
      "Total companies: %s, Batches: %s, Tasks queued: %s, Estimated sleep time: %.2f hours",
      total_companies,
      batches_processed,
      tasks_queued,
      estimated_sleep_hours,
    )

    return {
      "total_companies": total_companies,
      "batches_processed": batches_processed,
      "tasks_queued": tasks_queued,
      "batch_size": batch_size,
      "sleep_seconds": sleep_seconds,
      "estimated_completion_hours": estimated_sleep_hours,
    }


# Celery task 인스턴스 생성
bulk_ingest_and_regenerate_financial_statements = shared_task(
  base=BulkIngestAndRegenerateFinancialStatementsTask,
  bind=True,
)(BulkIngestAndRegenerateFinancialStatementsTask().run)
