"""
상장 회사 정보 조회 KRX Client
"""

import csv
import logging
from io import StringIO
from typing import Dict, List, Optional

from django.conf import settings

from common.clients.krx.base_krx_client import BaseKRXClient

logger = logging.getLogger(__name__)


class CompanyInfoKRXClient(BaseKRXClient):
  """상장 회사 정보 조회 클라이언트

    KRX로부터 상장 회사 목록 및 기본 정보를 조회합니다.
    """

  def get_download_url(self) -> str:
    """다운로드 URL 반환

        Returns:
            str: 회사 정보 데이터용 다운로드 URL
        """
    return settings.KRX_COMPANY_INGEST_DOWNLOAD_URL

  def _get_otp_payload(self, market_code: str, trade_date: Optional[str] = None, **kwargs) -> Dict[str, str]:
    """OTP 요청 페이로드 생성

        Args:
            market_code: 시장 코드 (STK: 코스피, KSQ: 코스닥)
            trade_date: 거래일 (YYYYMMDD 형식, None이면 현재일)

        Returns:
            Dict[str, str]: OTP 요청 페이로드
        """
    return {
      "locale": "ko_KR",
      "mktId": market_code,
      "trdDd": trade_date or "",
      "money": "1",
      "csvxls_isNo": "false",
      "name": "fileDown",
      "url": "dbms/MDC/STAT/standard/MDCSTAT03901",
    }

  def _get_download_payload(self,
                            otp_code: str,
                            market_code: str,
                            trade_date: Optional[str] = None,
                            **kwargs) -> Dict[str, str]:
    """데이터 다운로드 페이로드 생성

        Args:
            otp_code: OTP 코드
            market_code: 시장 코드
            trade_date: 거래일

        Returns:
            Dict[str, str]: 다운로드 요청 페이로드
        """
    return {
      "code": otp_code,
    }

  def fetch_company_list(self, market_code: str, trade_date: Optional[str] = None) -> List[Dict[str, str]]:
    """상장 회사 목록 조회

        Args:
            market_code: 시장 코드 (STK: 코스피, KSQ: 코스닥)
            trade_date: 거래일 (YYYYMMDD 형식, None이면 현재일)

        Returns:
            List[Dict[str, str]]: 회사 정보 리스트
        """
    try:
      csv_text = self.fetch_data(
        expect_json=False,
        encoding="euc-kr",
        market_code=market_code,
        trade_date=trade_date,
      )

      if not csv_text or not csv_text.strip():
        return []
      companies = self._parse_csv(csv_text)
      logger.info(f"상장 회사 조회 완료: {market_code} - {len(companies)}개 회사")
      return companies

    except Exception as e:
      logger.error(f"상장 회사 조회 실패: {market_code} - {e}")
      return []

  def _parse_csv(self, csv_text: str) -> List[Dict[str, str]]:
    """CSV 데이터 파싱

        CSV 헤더: 종목코드,종목명,시장구분,업종명,종가,대비,등락률,시가총액

        Args:
            csv_text: CSV 텍스트

        Returns:
            List[Dict[str, str]]: 파싱된 데이터
        """
    reader = csv.DictReader(StringIO(csv_text))
    entries: List[Dict[str, str]] = []

    for row in reader:
      entry = {
        "stock_code": self._parse_stock_code(row.get("종목코드", "")),
        "corp_name": row.get("종목명", "").strip(),
        "market": row.get("시장구분", "").strip(),
        "sector": row.get("업종명", "").strip(),
      }
      entries.append(entry)

    return entries

  @staticmethod
  def _parse_stock_code(value: str) -> str:
    """종목 코드 파싱 (6자리로 패딩)

        Args:
            value: 종목 코드

        Returns:
            str: 파싱된 종목 코드
        """
    return value.strip().zfill(6)
