"""
KRX 주식 정보 수집 태스크

KRX API를 통해 주식 정보를 수집하고 Stock 모델을 업데이트하는 Celery 태스크입니다.
이 태스크는 DART Company Ingest가 먼저 실행된 후 사용됩니다.
"""

import logging
from typing import Optional

from celery import shared_task
from stocks.services.krx_stock_ingest_service import KrxStockIngestService

from common.tasks.base_data_ingest_task import BaseDataIngestTask

logger = logging.getLogger(__name__)


class IngestKrxStockDataTask(BaseDataIngestTask):
  """KRX 주식 정보 수집 및 업데이트 Task"""

  name = "stocks.tasks.ingest_krx_stock_data"

  def run(self, trade_date: Optional[str] = None) -> dict:
    """KRX 주식 정보 수집 및 업데이트

    KRX API를 통해 주식 정보를 수집하고 Stock 모델을 업데이트합니다.
    이 태스크는 DART Company Ingest가 먼저 실행된 후 사용해야 합니다.

    Args:
      trade_date: 거래일 (YYYYMMDD 형식, None이면 현재일)

    Returns:
      dict: 수집 결과
        - stock_created: 생성된 주식 수
        - stock_updated: 업데이트된 주식 수
        - stock_delisted: 상장폐지 처리된 주식 수
        - total_entries: 처리한 항목 수
    """
    logger.info("KRX 주식 정보 수집 태스크 시작")

    try:
      service = KrxStockIngestService()
      result = service.perform(trade_date=trade_date)

      logger.info(
        f"KRX 주식 정보 수집 태스크 완료 - "
        f"주식 생성: {result.get('stock_created', 0)}, "
        f"주식 업데이트: {result.get('stock_updated', 0)}, "
        f"상장폐지: {result.get('stock_delisted', 0)}, "
        f"전체: {result.get('total_entries', 0)}"
      )

      return result

    except Exception as e:
      logger.error(f"KRX 주식 정보 수집 태스크 실패: {e}", exc_info=True)
      raise


# Celery task 인스턴스 생성
ingest_krx_stock_data = shared_task(base=IngestKrxStockDataTask, bind=True)(IngestKrxStockDataTask().run)
