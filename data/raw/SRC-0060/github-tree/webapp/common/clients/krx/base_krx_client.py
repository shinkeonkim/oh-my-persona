"""
Base KRX Client

KRX API 공통 로직을 제공하는 베이스 클라이언트
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class BaseKRXClient(ABC):
  """KRX API 베이스 클라이언트

    OTP 요청, 데이터 다운로드 등 공통 로직을 제공합니다.
    """

  def __init__(self):
    self.otp_url = settings.KRX_OTP_URL
    self.session = requests.Session()
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": settings.KRX_REFERER,
      "Origin": settings.KRX_ORIGIN,
    }
    self.timeout = 30
    self.max_retries = 3
    self.backoff_seconds = 2

  @abstractmethod
  def get_download_url(self) -> str:
    """다운로드 URL 반환 (서브클래스에서 구현)

        Returns:
            str: 다운로드 URL
        """
    pass

  @abstractmethod
  def _get_otp_payload(self, **kwargs) -> Dict[str, str]:
    """OTP 요청 페이로드 생성 (서브클래스에서 구현)

        Args:
            **kwargs: API별 필요한 파라미터

        Returns:
            Dict[str, str]: OTP 요청 페이로드
        """
    pass

  @abstractmethod
  def _get_download_payload(self, otp_code: str, **kwargs) -> Dict[str, str]:
    """데이터 다운로드 페이로드 생성 (서브클래스에서 구현)

        Args:
            otp_code: OTP 코드
            **kwargs: API별 필요한 파라미터

        Returns:
            Dict[str, str]: 다운로드 요청 페이로드
        """
    pass

  def _request_otp(self, **kwargs) -> str:
    """OTP 코드 요청

        Args:
            **kwargs: API별 필요한 파라미터

        Returns:
            str: OTP 코드

        Raises:
            requests.RequestException: 요청 실패 시
        """
    payload = self._get_otp_payload(**kwargs)

    for attempt in range(1, self.max_retries + 1):
      try:
        response = self.session.post(
          self.otp_url,
          data=payload,
          headers=self.headers,
          timeout=self.timeout,
        )
        response.raise_for_status()
        otp_code = response.text.strip()

        logger.debug(f"OTP 요청 성공 (시도 {attempt}/{self.max_retries})")
        return otp_code

      except requests.RequestException as e:
        logger.warning(f"OTP 요청 실패 (시도 {attempt}/{self.max_retries}): {e}")
        if attempt < self.max_retries:
          time.sleep(self.backoff_seconds)
        else:
          raise

    raise requests.RequestException("OTP 요청 최대 재시도 횟수 초과")

  def _download_data(self, otp_code: str, expect_json: bool = True, encoding: str = "utf-8", **kwargs):
    """데이터 다운로드

        Args:
            otp_code: OTP 코드
            expect_json: JSON 응답 여부
            encoding: 응답 인코딩 (기본값: utf-8)
            **kwargs: API별 필요한 파라미터

        Returns:
            dict 또는 str: 응답 데이터

        Raises:
            requests.RequestException: 요청 실패 시
        """
    payload = self._get_download_payload(otp_code, **kwargs)

    for attempt in range(1, self.max_retries + 1):
      try:
        response = self.session.post(
          self.get_download_url(),
          data=payload,
          headers=self.headers,
          timeout=self.timeout,
        )
        response.raise_for_status()

        if expect_json:
          return response.json()
        else:
          return response.content.decode(encoding)

      except requests.RequestException as e:
        logger.warning(f"데이터 다운로드 실패 (시도 {attempt}/{self.max_retries}): {e}")
        if attempt < self.max_retries:
          time.sleep(self.backoff_seconds)
        else:
          raise

    raise requests.RequestException("데이터 다운로드 최대 재시도 횟수 초과")

  def fetch_data(
    self,
    expect_json: bool = True,
    encoding: str = "utf-8",
    sleep_after: Optional[float] = None,
    **kwargs,
  ):
    """OTP 요청 후 데이터 다운로드 (통합 메서드)

    Args:
      expect_json: JSON 응답 여부
      encoding: 응답 인코딩
      sleep_after: 요청 후 대기 시간 (초)
      **kwargs: API별 필요한 파라미터

    Returns:
        dict 또는 str: 응답 데이터
    """
    # OTP 요청
    otp_code = self._request_otp(**kwargs)

    # 선택적 딜레이
    if sleep_after:
      time.sleep(sleep_after)

    # 데이터 다운로드
    data = self._download_data(otp_code, expect_json, encoding, **kwargs)

    return data

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
