"""
주식 가격 데이터 조회 KRX Client
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, List

from django.conf import settings

from common.clients.krx.base_krx_client import BaseKRXClient

logger = logging.getLogger(__name__)


class StockPriceKRXClient(BaseKRXClient):
  """주식 가격 데이터 조회 클라이언트

  - KRX로부터 일자별 주식 시장 가격 데이터를 조회합니다.
  """

  def get_download_url(self) -> str:
    """다운로드 URL 반환

        Returns:
            str: 주식 가격 데이터용 다운로드 URL
        """
    return settings.KRX_STOCK_PRICE_DOWNLOAD_URL

  def _get_otp_payload(self, trade_date: date, market_code: str, **kwargs) -> Dict[str, str]:
    """OTP 요청 페이로드 생성

        Args:
            trade_date: 거래일
            market_code: 시장 코드 (STK: 코스피, KSQ: 코스닥)

        Returns:
            Dict[str, str]: OTP 요청 페이로드
        """
    return {
      "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
      "mktId": market_code,
      "share": "1",
      "csvxls_isNo": "false",
      "trdDd": trade_date.strftime("%Y%m%d"),
      "locale": "ko_KR",
      "name": "fileDown",
      "money": "1",
      "url": "dbms/MDC/STAT/standard/MDCSTAT01501",
    }

  def _get_download_payload(self, otp_code: str, trade_date: date, market_code: str, **kwargs) -> Dict[str, str]:
    """데이터 다운로드 페이로드 생성

        Args:
            otp_code: OTP 코드
            trade_date: 거래일
            market_code: 시장 코드

        Returns:
            Dict[str, str]: 다운로드 요청 페이로드
        """
    return {
      "bld": "dbms/MDC/STAT/standard/MDCSTAT01501",
      "mktId": market_code,
      "share": "1",
      "csvxls_isNo": "false",
      "trdDd": trade_date.strftime("%Y%m%d"),
      "code": otp_code,
    }

  def fetch_daily_prices(self, trade_date: date, market_code: str) -> List[Dict]:
    """특정 일자의 시장 가격 데이터 조회

        Args:
            trade_date: 거래일
            market_code: 시장 코드 (STK: 코스피, KSQ: 코스닥)

        Returns:
            List[Dict]: 주식 가격 데이터 리스트
        """
    try:
      data = self.fetch_data(
        expect_json=True,
        trade_date=trade_date,
        market_code=market_code,
      )

      items = data.get("OutBlock_1", [])
      logger.info(f"주식 가격 조회 완료: {trade_date} {market_code} - {len(items)}개 종목")
      return items

    except Exception as e:
      logger.error(f"주식 가격 조회 실패: {trade_date} {market_code} - {e}")
      return []

  @staticmethod
  def parse_decimal(value: str) -> Decimal:
    """문자열을 Decimal로 변환

        Args:
            value: 숫자 문자열

        Returns:
            Decimal: 변환된 값
        """
    if not value or value == "-":
      return Decimal("0")
    cleaned = value.replace(",", "").strip()
    return Decimal(cleaned)

  @staticmethod
  def parse_int(value: str) -> int:
    """문자열을 int로 변환

        Args:
            value: 숫자 문자열

        Returns:
            int: 변환된 값
        """
    if not value or value == "-":
      return 0
    cleaned = value.replace(",", "").strip()
    return int(float(cleaned))
