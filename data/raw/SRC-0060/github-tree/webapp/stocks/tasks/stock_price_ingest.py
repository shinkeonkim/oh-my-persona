"""
주식 가격 데이터 수집 Celery Task
"""

import logging
from datetime import datetime, timedelta

from celery import shared_task
from stocks.services.stock_price_ingest_service import StockPriceIngestService

from common.tasks.base_data_ingest_task import BaseDataIngestTask

logger = logging.getLogger(__name__)


class IngestStockPricesForDateTask(BaseDataIngestTask):
  """특정 일자의 주식 가격 데이터를 수집하는 Task"""

  name = "stocks.tasks.ingest_stock_prices_for_date"
  max_retries = 3
  default_retry_delay = 300  # 5분

  def run(self, trade_date_str: str, markets: list | None = None):
    """특정 일자의 주식 가격 데이터를 수집

    Args:
        trade_date_str: 거래일 (YYYY-MM-DD 형식)
        markets: 시장 코드 리스트 (None이면 기본값 사용)

    Returns:
        dict: 수집 결과
    """
    try:
      # 문자열을 date 객체로 변환
      trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d").date()

      logger.info(f"주식 가격 데이터 수집 시작: {trade_date}")

      service = StockPriceIngestService()
      try:
        results = service.ingest_daily_prices(trade_date, markets)
        logger.info(f"주식 가격 데이터 수집 완료: {trade_date}, 결과: {results}")
        return {
          "status": "success",
          "trade_date": trade_date_str,
          "results": results,
        }
      finally:
        service.close()

    except Exception as exc:
      logger.error(f"주식 가격 데이터 수집 실패: {trade_date_str}, 에러: {exc}")
      # 재시도
      raise self.retry(exc=exc)


class IngestStockPricesForDateRangeTask(BaseDataIngestTask):
  """날짜 범위의 주식 가격 데이터를 수집하는 Task"""

  name = "stocks.tasks.ingest_stock_prices_for_date_range"

  def run(self, start_date_str: str, end_date_str: str, markets: list | None = None):
    """날짜 범위의 주식 가격 데이터를 수집

    Args:
        start_date_str: 시작일 (YYYY-MM-DD 형식)
        end_date_str: 종료일 (YYYY-MM-DD 형식)
        markets: 시장 코드 리스트 (None이면 기본값 사용)

    Returns:
        dict: 전체 작업 정보
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    logger.info(f"주식 가격 데이터 범위 수집 시작: {start_date} ~ {end_date}")

    # 날짜 범위의 각 일자에 대해 개별 Task 실행
    task_ids = []
    current_date = start_date

    while current_date <= end_date:
      # 주말 제외 (토요일: 5, 일요일: 6)
      if current_date.weekday() < 5:
        task = ingest_stock_prices_for_date.delay(trade_date_str=current_date.strftime("%Y-%m-%d"), markets=markets)
        task_ids.append(task.id)
        logger.info(f"Task 생성: {current_date}, Task ID: {task.id}")

      current_date += timedelta(days=1)

    return {
      "status": "dispatched",
      "start_date": start_date_str,
      "end_date": end_date_str,
      "task_count": len(task_ids),
      "task_ids": task_ids,
    }


class IngestTodayStockPricesTask(BaseDataIngestTask):
  """오늘 날짜의 주식 가격 데이터를 수집하는 Task"""

  name = "stocks.tasks.ingest_today_stock_prices"

  def run(self, markets: list | None = None):
    """오늘 날짜의 주식 가격 데이터를 수집

    매시간 자동으로 실행되도록 Celery Beat에 등록하여 사용

    Args:
        markets: 시장 코드 리스트 (None이면 기본값 사용)

    Returns:
        dict: 작업 정보
    """
    today = datetime.now().date()

    # 주말이면 실행하지 않음
    if today.weekday() >= 5:  # 토요일(5) 또는 일요일(6)
      logger.info(f"주말이므로 실행하지 않음: {today}")
      return {
        "status": "skipped",
        "reason": "weekend",
        "date": today.strftime("%Y-%m-%d"),
      }

    logger.info(f"오늘 주식 가격 데이터 수집: {today}")

    task = ingest_stock_prices_for_date.delay(trade_date_str=today.strftime("%Y-%m-%d"), markets=markets)

    return {
      "status": "dispatched",
      "trade_date": today.strftime("%Y-%m-%d"),
      "task_id": task.id,
    }


class IngestYesterdayStockPricesTask(BaseDataIngestTask):
  """어제 날짜의 주식 가격 데이터를 수집하는 Task"""

  name = "stocks.tasks.ingest_yesterday_stock_prices"

  def run(self, markets: list | None = None):
    """어제 날짜의 주식 가격 데이터를 수집

    매일 자동으로 실행되도록 Celery Beat에 등록하여 사용

    Args:
        markets: 시장 코드 리스트 (None이면 기본값 사용)

    Returns:
        dict: 작업 정보
    """
    yesterday = (datetime.now() - timedelta(days=1)).date()

    # 주말이면 금요일 데이터 수집
    if yesterday.weekday() == 5:  # 토요일
      yesterday = yesterday - timedelta(days=1)
    elif yesterday.weekday() == 6:  # 일요일
      yesterday = yesterday - timedelta(days=2)

    logger.info(f"어제 주식 가격 데이터 수집: {yesterday}")

    task = ingest_stock_prices_for_date.delay(trade_date_str=yesterday.strftime("%Y-%m-%d"), markets=markets)

    return {
      "status": "dispatched",
      "trade_date": yesterday.strftime("%Y-%m-%d"),
      "task_id": task.id,
    }


# Celery task 인스턴스 생성
ingest_stock_prices_for_date = shared_task(
  bind=True, name="stocks.tasks.ingest_stock_prices_for_date", base=IngestStockPricesForDateTask
)(IngestStockPricesForDateTask().run)

ingest_stock_prices_for_date_range = shared_task(
  bind=True, name="stocks.tasks.ingest_stock_prices_for_date_range", base=IngestStockPricesForDateRangeTask
)(IngestStockPricesForDateRangeTask().run)

ingest_today_stock_prices = shared_task(
  bind=True, name="stocks.tasks.ingest_today_stock_prices", base=IngestTodayStockPricesTask
)(IngestTodayStockPricesTask().run)

ingest_yesterday_stock_prices = shared_task(
  bind=True, name="stocks.tasks.ingest_yesterday_stock_prices", base=IngestYesterdayStockPricesTask
)(IngestYesterdayStockPricesTask().run)
