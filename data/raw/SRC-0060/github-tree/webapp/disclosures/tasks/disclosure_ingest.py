from __future__ import annotations

import logging

from django.db import transaction

import requests
from celery import shared_task

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.models import Company

from ..services.disclosure_service import CompanyDisclosureService

logger = logging.getLogger(__name__)


class IngestCompanyDisclosuresTask(BaseDataIngestTask):
  """회사 공시 정보 수집 Task"""

  name = "companies.tasks.ingest_company_disclosures"
  autoretry_for = (requests.RequestException, )
  retry_backoff = True
  max_retries = 3

  def run(
    self,
    company_id: int,
    begin_date: str,
    end_date: str,
    refresh_existing: bool = False,
    page_count: int = 100,
  ) -> dict:
    """회사 공시 정보 수집

    Args:
        company_id: 회사 ID
        begin_date: 시작일
        end_date: 종료일
        refresh_existing: 기존 데이터 갱신 여부
        page_count: 페이지당 항목 수

    Returns:
        dict: 수집 결과
            - created: 생성된 공시 수
            - updated: 업데이트된 공시 수
            - skipped: 스킵된 공시 수
    """
    try:
      company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
      logger.warning("Company with id %s not found; skipping disclosure ingest.", company_id)
      return {"created": 0, "updated": 0, "skipped": 0}

    service = CompanyDisclosureService()

    with transaction.atomic():
      result = service.perform(
        company=company,
        begin_date=begin_date,
        end_date=end_date,
        page_count=page_count,
        refresh_existing=refresh_existing,
      )

    logger.info(
      "Disclosure ingest completed for company %s: created=%s updated=%s skipped=%s",
      company.id,
      result.get("created"),
      result.get("updated"),
      result.get("skipped"),
    )
    return result


# Celery task 인스턴스 생성
ingest_company_disclosures = shared_task(base=IngestCompanyDisclosuresTask,
                                         bind=True)(IngestCompanyDisclosuresTask().run)
