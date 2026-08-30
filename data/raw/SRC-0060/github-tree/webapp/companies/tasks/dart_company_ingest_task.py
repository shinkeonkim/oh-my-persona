"""
DART 회사 정보 수집 태스크

OpenDart API를 통해 회사 정보를 수집하고 Company 모델을 업데이트하는 Celery 태스크입니다.
"""

import logging

from celery import shared_task

from common.tasks.base_data_ingest_task import BaseDataIngestTask
from companies.services.dart_company_ingest_service import DartCompanyIngestService

logger = logging.getLogger(__name__)


class IngestDartCompanyDataTask(BaseDataIngestTask):
  """DART 회사 정보 수집 및 업데이트 Task"""

  name = "companies.tasks.ingest_dart_company_data"

  def run(self) -> dict:
    """DART 회사 정보 수집 및 업데이트

    OpenDart API를 통해 회사 정보를 수집하고 Company 모델을 업데이트합니다.
    - DART: corp_code, english_name, primary_stock_code 수집

    Returns:
      dict: 수집 결과
        - companies_created: 생성된 회사 수
        - companies_updated: 업데이트된 회사 수
        - total_dart_data: 처리한 DART 데이터 수
    """
    logger.info("DART 회사 정보 수집 태스크 시작")

    try:
      service = DartCompanyIngestService()
      result = service.perform()

      logger.info(
        f"DART 회사 정보 수집 태스크 완료 - "
        f"생성: {result.get('companies_created', 0)}, "
        f"업데이트: {result.get('companies_updated', 0)}, "
        f"전체 DART: {result.get('total_dart_data', 0)}"
      )

      return result

    except Exception as e:
      logger.error(f"DART 회사 정보 수집 태스크 실패: {e}", exc_info=True)
      raise


# Celery task 인스턴스 생성
ingest_dart_company_data = shared_task(
  bind=True, name="companies.tasks.ingest_dart_company_data", base=IngestDartCompanyDataTask
)(IngestDartCompanyDataTask().run)
