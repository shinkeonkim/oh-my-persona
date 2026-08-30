"""
Delisted Stock Ingest Task

상장 폐지 종목 정보 수집 Celery 태스크
"""

import logging
from datetime import datetime
from typing import Dict

from celery import shared_task
from stocks.services.delisted_stock_ingest_service import DelistedStockIngestService

from common.tasks.base_data_ingest_task import BaseDataIngestTask

logger = logging.getLogger(__name__)


class IngestDelistedStocksTask(BaseDataIngestTask):
  """상장 폐지 종목 정보 수집 태스크"""

  name = "stocks.ingest_delisted_stocks"
  max_retries = 3
  default_retry_delay = 60

  def run(
    self,
    start_date: str,
    end_date: str,
    market_id: str = "ALL",
  ) -> Dict[str, int]:
    """상장 폐지 종목 정보 수집

    Args:
        start_date: 조회 시작일 (YYYYMMDD 형식)
        end_date: 조회 종료일 (YYYYMMDD 형식)
        market_id: 시장 구분 (ALL, STK=KOSPI, KSQ=KOSDAQ)

    Returns:
        Dict[str, int]: 수집 결과 통계
            - total: 총 조회된 종목 수
            - created: 새로 생성된 종목 수
            - updated: 업데이트된 종목 수
            - skipped: 스킵된 종목 수

    Raises:
        Exception: 수집 실패 시 재시도
    """
    logger.info(
      f"[Task] 상장 폐지 종목 정보 수집 태스크 시작: "
      f"start_date={start_date}, end_date={end_date}, market_id={market_id}"
    )

    try:
      service = DelistedStockIngestService()
      stats = service.perform(
        start_date=start_date,
        end_date=end_date,
        market_id=market_id,
      )

      logger.info(
        f"[Task] 상장 폐지 종목 정보 수집 태스크 완료: "
        f"total={stats['total']}, created={stats['created']}, "
        f"updated={stats['updated']}, skipped={stats['skipped']}"
      )

      return stats

    except Exception as exc:
      logger.error(f"[Task] 상장 폐지 종목 정보 수집 태스크 실패: {exc}")
      # 재시도
      raise self.retry(exc=exc)


class IngestDelistedStocksAutoTask(BaseDataIngestTask):
  """상장 폐지 종목 정보 자동 수집 태스크 (스케줄 실행용)"""

  name = "stocks.ingest_delisted_stocks_auto"

  def run(self, market_id: str = "ALL") -> Dict:
    """상장 폐지 종목 정보 자동 수집

    오늘 하루의 상장 폐지 종목 정보를 수집합니다.

    Args:
        market_id: 시장 구분 (ALL, STK=KOSPI, KSQ=KOSDAQ)

    Returns:
        Dict[str, int]: 수집 결과 통계
    """
    # 오늘 날짜
    today = datetime.now().date()

    # YYYYMMDD 형식으로 변환
    start_date_str = today.strftime("%Y%m%d")
    end_date_str = today.strftime("%Y%m%d")

    logger.info(f"상장 폐지 종목 자동 수집: start_date={start_date_str}, end_date={end_date_str}, market_id={market_id}")

    # 기존 태스크 호출
    task = ingest_delisted_stocks.delay(
      start_date=start_date_str,
      end_date=end_date_str,
      market_id=market_id,
    )

    return {
      "status": "dispatched",
      "task_id": task.id,
      "start_date": start_date_str,
      "end_date": end_date_str,
      "market_id": market_id,
    }


# Celery task 인스턴스 생성
ingest_delisted_stocks = shared_task(
  bind=True, name="stocks.tasks.ingest_delisted_stocks", base=IngestDelistedStocksTask
)(IngestDelistedStocksTask().run)

ingest_delisted_stocks_auto = shared_task(
  bind=True, name="stocks.tasks.ingest_delisted_stocks_auto", base=IngestDelistedStocksAutoTask
)(IngestDelistedStocksAutoTask().run)
