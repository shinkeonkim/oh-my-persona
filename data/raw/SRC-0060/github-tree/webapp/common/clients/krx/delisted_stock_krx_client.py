"""
Delisted Stock KRX Client

상장 폐지 종목 정보를 KRX API에서 가져오는 클라이언트
"""

import logging
import time
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class DelistedStockKRXClient:
  """상장 폐지 종목 정보 KRX 클라이언트

    KRX API를 통해 상장 폐지 종목 정보를 가져옵니다.
    OTP가 필요 없는 API이므로 BaseKRXClient를 상속하지 않습니다.
    """

  def __init__(self):
    self.url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    self.session = requests.Session()
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader",
      "Origin": "https://data.krx.co.kr",
    }
    self.timeout = 30
    self.max_retries = 3
    self.backoff_seconds = 2

  def fetch_delisted_stocks(
    self,
    start_date: str,
    end_date: str,
    market_id: str = "ALL",
    isu_cd: str = "ALL",
    share: str = "1",
  ) -> List[Dict]:
    """상장 폐지 종목 정보 가져오기

        Args:
            start_date: 조회 시작일 (YYYYMMDD)
            end_date: 조회 종료일 (YYYYMMDD)
            market_id: 시장 구분 (ALL, STK=KOSPI, KSQ=KOSDAQ)
            isu_cd: 종목 코드 (ALL 또는 특정 종목 코드)
            share: 주식 포함 여부 (1=포함, 0=제외)

        Returns:
            List[Dict]: 상장 폐지 종목 정보 리스트

        Raises:
            requests.RequestException: 요청 실패 시
        """
    payload = {
      "bld": "dbms/MDC/STAT/issue/MDCSTAT23801",
      "locale": "ko_KR",
      "mktId": market_id,
      "tboxisuCd_finder_listdelisu0_0": "전체",
      "isuCd": isu_cd,
      "isuCd2": "ALL",
      "codeNmisuCd_finder_listdelisu0_0": "",
      "param1isuCd_finder_listdelisu0_0": "",
      "strtDd": start_date,
      "endDd": end_date,
      "share": share,
      "csvxls_isNo": "true",
    }

    for attempt in range(1, self.max_retries + 1):
      try:
        logger.info(
          f"상장 폐지 종목 정보 요청 시작 (시도 {attempt}/{self.max_retries}): "
          f"start_date={start_date}, end_date={end_date}, market_id={market_id}"
        )

        response = self.session.post(
          self.url,
          data=payload,
          headers=self.headers,
          timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        # 응답 데이터 검증
        if not isinstance(data, dict):
          raise ValueError(f"예상하지 못한 응답 형식: {type(data)}")

        output = data.get("output", [])
        logger.info(f"상장 폐지 종목 {len(output)}개 조회 완료")

        return output

      except requests.RequestException as e:
        logger.warning(f"상장 폐지 종목 정보 요청 실패 (시도 {attempt}/{self.max_retries}): {e}")
        if attempt < self.max_retries:
          time.sleep(self.backoff_seconds)
        else:
          logger.error(f"상장 폐지 종목 정보 요청 최종 실패: {e}")
          raise

      except (ValueError, KeyError) as e:
        logger.error(f"상장 폐지 종목 정보 응답 데이터 파싱 실패: {e}")
        raise

    raise requests.RequestException("상장 폐지 종목 정보 요청 최대 재시도 횟수 초과")

  def close(self):
    """세션 종료"""
    if self.session:
      self.session.close()

  def __enter__(self):
    """Context manager 진입"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager 종료"""
    self.close()
