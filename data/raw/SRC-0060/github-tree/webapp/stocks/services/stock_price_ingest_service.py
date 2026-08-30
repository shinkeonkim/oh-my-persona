"""
주식 가격 데이터 수집 서비스

KRX로부터 일자별 주식 가격 데이터를 수집하여 저장합니다.
"""

import logging
import time
from datetime import date
from typing import Dict, List, Optional

from django.conf import settings
from django.db import transaction

from stocks.models import Market, Stock, StockPrice

from common.clients.krx import StockPriceKRXClient

logger = logging.getLogger(__name__)


class StockPriceIngestService:
  """주식 가격 데이터 수집 및 저장 서비스"""

  def __init__(self):
    self.client = StockPriceKRXClient()
    # Market code -> Market 객체 매핑 캐시
    self.market_cache: Dict[str, Market] = {}
    # Stock code -> Stock 객체 매핑 캐시
    self.stock_cache: Dict[str, Stock] = {}

  def _get_market(self, market_code: str) -> Optional[Market]:
    """Market 코드로 Market 객체 조회 (캐싱)"""
    if market_code not in self.market_cache:
      try:
        self.market_cache[market_code] = Market.objects.get(code=market_code)
      except Market.DoesNotExist:
        logger.error(f"Market not found: {market_code}")
        return None
    return self.market_cache[market_code]

  def _get_stock(self, stock_code: str) -> Optional[Stock]:
    """Stock 코드로 Stock 객체 조회 (캐싱)"""
    if stock_code not in self.stock_cache:
      try:
        self.stock_cache[stock_code] = Stock.objects.get(code=stock_code)
      except Stock.DoesNotExist:
        logger.warning(f"Stock not found: {stock_code}")
        return None
    return self.stock_cache[stock_code]

  def _create_stock_price_from_krx_data(self, trade_date: date, market: Market, item: dict) -> Optional[StockPrice]:
    """KRX 데이터로부터 StockPrice 객체 생성"""
    try:
      stock_code = item.get("ISU_SRT_CD", "").strip()
      if not stock_code:
        logger.warning(f"Stock code missing in item: {item}")
        return None

      # Stock 객체 조회
      stock = self._get_stock(stock_code)
      if not stock:
        logger.warning(f"Stock not found: {stock_code}")
        # Stock이 없는 경우 스킵 (회사 메타데이터 먼저 수집 필요)
        return None

      close_price = StockPriceKRXClient.parse_decimal(item.get("TDD_CLSPRC", "0"))
      diff = StockPriceKRXClient.parse_decimal(item.get("CMPPREVDD_PRC", "0"))
      change_rate = StockPriceKRXClient.parse_decimal(item.get("FLUC_RT", "0"))
      open_price = StockPriceKRXClient.parse_decimal(item.get("TDD_OPNPRC", "0"))
      high_price = StockPriceKRXClient.parse_decimal(item.get("TDD_HGPRC", "0"))
      low_price = StockPriceKRXClient.parse_decimal(item.get("TDD_LWPRC", "0"))
      volume = StockPriceKRXClient.parse_int(item.get("ACC_TRDVOL", "0"))
      value = StockPriceKRXClient.parse_int(item.get("ACC_TRDVAL", "0"))
      market_cap = StockPriceKRXClient.parse_int(item.get("MKTCAP", "0"))
      shares = StockPriceKRXClient.parse_int(item.get("LIST_SHRS", "0"))

      if close_price == 0 and volume == 0 and market_cap == 0:
        return None

      return StockPrice(
        trade_date=trade_date,
        market=market,
        stock=stock,
        close_price=close_price,
        diff=diff,
        change_rate=change_rate,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        volume=volume,
        value=value,
        market_cap=market_cap,
        shares=shares,
      )
    except Exception as e:
      logger.error(f"StockPrice 객체 생성 실패: {e}, item: {item}")
      return None

  @transaction.atomic
  def ingest_daily_prices(self, trade_date: date, markets: Optional[List[str]] = None) -> dict:
    """특정 일자의 주식 가격 데이터 수집 및 저장

        Args:
            trade_date: 거래일
            markets: 시장 코드 리스트 (None이면 기본값 사용)

        Returns:
            dict: 수집 결과 (market별 저장된 레코드 수)
        """
    if markets is None:
      markets = settings.KRX_DEFAULT_MARKETS

    results = {}

    for market_code in markets:
      # Market 객체 조회
      market = self._get_market(market_code)
      if not market:
        logger.error(f"Market 조회 실패: {market_code}")
        results[market_code] = {"status": "error", "count": 0, "error": "Market not found"}
        continue

      # 이미 데이터가 있는지 확인
      existing_count = (StockPrice.objects.filter(trade_date=trade_date, market=market).count())

      if existing_count > 0:
        logger.info(f"이미 데이터 존재: {trade_date} {market_code} - {existing_count}개")
        results[market_code] = {"status": "skipped", "count": existing_count}
        continue

      # KRX에서 데이터 조회
      items = self.client.fetch_daily_prices(trade_date, market_code)

      if not items:
        logger.warning(f"데이터 없음: {trade_date} {market_code}")
        results[market_code] = {"status": "no_data", "count": 0}
        continue

      # StockPrice 객체 생성
      stock_prices = []
      skipped_count = 0
      for item in items:
        stock_price = self._create_stock_price_from_krx_data(trade_date, market, item)
        if stock_price:
          stock_prices.append(stock_price)
        else:
          skipped_count += 1

      # 데이터베이스에 저장 (PostgreSQL)
      if stock_prices:
        StockPrice.objects.bulk_create(stock_prices, ignore_conflicts=True)
        logger.info(f"저장 완료: {trade_date} {market_code} - {len(stock_prices)}개 저장, {skipped_count}개 스킵")
        results[market_code] = {
          "status": "success",
          "count": len(stock_prices),
          "skipped": skipped_count,
        }
      else:
        logger.warning(f"저장할 데이터 없음: {trade_date} {market_code} - 모두 스킵됨")
        results[market_code] = {
          "status": "no_valid_data",
          "count": 0,
          "skipped": skipped_count,
        }

      # 요청 간 딜레이
      time.sleep(settings.KRX_SLEEP)

    return results

  def close(self):
    """리소스 정리"""
    self.client.close()
