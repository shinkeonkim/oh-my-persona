"""
Delisted Stock Long Period Ingest Task

2년을 초과하는 긴 기간의 상장 폐지 종목 정보를 수집하는 Celery 태스크
KRX API의 2년 제한을 우회하기 위해 1년 단위로 끊어서 조회합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from celery import shared_task
from stocks.services.delisted_stock_ingest_service import DelistedStockIngestService

from common.tasks.base_data_ingest_task import BaseDataIngestTask

logger = logging.getLogger(__name__)


class IngestDelistedStocksLongPeriodTask(BaseDataIngestTask):
  """2년 초과 기간의 상장 폐지 종목 정보 수집 태스크"""

  name = "stocks.ingest_delisted_stocks_long_period"
  max_retries = 3
  default_retry_delay = 60

  def run(
    self,
    start_date: str,
    end_date: str,
    market_id: str = "ALL",
  ) -> Dict[str, int]:
    """2년 초과 기간의 상장 폐지 종목 정보 수집

    KRX API는 최대 2년까지만 조회 가능하므로, 주어진 기간을 1년 단위로 나누어 조회합니다.

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
            - stock_updated: Stock 업데이트된 수
            - stock_delisted: Stock 상장폐지 처리된 수
            - periods: 조회한 기간 수

    Raises:
        Exception: 수집 실패 시 재시도
    """
    logger.info(
      f"[Task] 상장 폐지 종목 정보 장기 수집 태스크 시작: "
      f"start_date={start_date}, end_date={end_date}, market_id={market_id}"
    )

    try:
      # 날짜 파싱
      start_dt = datetime.strptime(start_date, "%Y%m%d")
      end_dt = datetime.strptime(end_date, "%Y%m%d")

      # 1년 단위로 기간 분할
      periods = self._split_period_by_year(start_dt, end_dt)

      # 누적 통계
      total_stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "stock_updated": 0,
        "stock_delisted": 0,
        "periods": len(periods),
      }

      # 각 기간별로 수집
      service = DelistedStockIngestService()
      for idx, (period_start, period_end) in enumerate(periods, 1):
        period_start_str = period_start.strftime("%Y%m%d")
        period_end_str = period_end.strftime("%Y%m%d")

        logger.info(f"[Task] 기간 {idx}/{len(periods)} 수집 시작: "
                    f"{period_start_str} ~ {period_end_str}")

        stats = service.perform(
          start_date=period_start_str,
          end_date=period_end_str,
          market_id=market_id,
        )

        # 누적
        total_stats["total"] += stats.get("total", 0)
        total_stats["created"] += stats.get("created", 0)
        total_stats["updated"] += stats.get("updated", 0)
        total_stats["skipped"] += stats.get("skipped", 0)
        total_stats["stock_updated"] += stats.get("stock_updated", 0)
        total_stats["stock_delisted"] += stats.get("stock_delisted", 0)

        logger.info(
          f"[Task] 기간 {idx}/{len(periods)} 수집 완료: "
          f"total={stats['total']}, created={stats['created']}, "
          f"updated={stats['updated']}, skipped={stats['skipped']}"
        )

      service.close()

      logger.info(
        f"[Task] 상장 폐지 종목 정보 장기 수집 태스크 완료: "
        f"total={total_stats['total']}, created={total_stats['created']}, "
        f"updated={total_stats['updated']}, skipped={total_stats['skipped']}, "
        f"stock_updated={total_stats['stock_updated']}, "
        f"stock_delisted={total_stats['stock_delisted']}, "
        f"periods={total_stats['periods']}"
      )

      return total_stats

    except Exception as exc:
      logger.error(f"[Task] 상장 폐지 종목 정보 장기 수집 태스크 실패: {exc}")
      # 재시도
      raise self.retry(exc=exc)

  def _split_period_by_year(self, start_dt: datetime, end_dt: datetime) -> list:
    """기간을 1년 단위로 분할

    Args:
        start_dt: 시작일
        end_dt: 종료일

    Returns:
        list: [(시작일, 종료일), ...] 튜플 리스트
    """
    periods = []
    current_start = start_dt

    while current_start < end_dt:
      # 1년 후 날짜 계산
      current_end = current_start + timedelta(days=365)

      # 마지막 기간이면 end_dt로 조정
      if current_end > end_dt:
        current_end = end_dt

      periods.append((current_start, current_end))
      current_start = current_end + timedelta(days=1)

    return periods


# Celery task 인스턴스 생성
ingest_delisted_stocks_long_period = shared_task(base=IngestDelistedStocksLongPeriodTask,
                                                 bind=True)(IngestDelistedStocksLongPeriodTask().run)
