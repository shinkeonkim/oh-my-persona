"""
Base OpenDart Client

OpenDart API 공통 로직을 제공하는 베이스 클라이언트
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class BaseOpenDartClient(ABC):
  """OpenDart API 베이스 클라이언트
  - API 호출, 재시도, 에러 처리 등 공통 로직을 제공합니다.
  """

  def __init__(self, api_key: Optional[str] = None):
    """
    Args:
      api_key: OpenDart API 키 (None이면 settings에서 가져옴)
    """
    self.api_key = api_key or settings.DART_API_KEY
    if not self.api_key:
      raise ValueError("DART_API_KEY is not configured.")

    self.session = requests.Session()
    self.timeout = 30
    self.max_retries = 3
    self.backoff_seconds = 2

  @abstractmethod
  def get_api_url(self) -> str:
    """API URL 반환 (서브클래스에서 구현)

        Returns:
            str: API 엔드포인트 URL
        """
    pass

  def _get_base_params(self) -> Dict[str, str]:
    """기본 파라미터 반환 (API 키 포함)

        Returns:
            Dict[str, str]: 기본 파라미터
        """
    return {
      "crtfc_key": self.api_key,
    }

  def _build_params(self, **kwargs) -> Dict[str, Any]:
    """요청 파라미터 생성

        Args:
            **kwargs: API별 필요한 파라미터

        Returns:
            Dict[str, Any]: 요청 파라미터
        """
    params = self._get_base_params()
    params.update(kwargs)
    return params

  def fetch_data(
    self,
    params: Optional[Dict[str, Any]] = None,
    expect_json: bool = True,
    **kwargs,
  ) -> Any:
    """데이터 조회 (통합 메서드)

        Args:
            params: 요청 파라미터 (None이면 kwargs로부터 생성)
            expect_json: JSON 응답 여부
            **kwargs: API별 필요한 파라미터

        Returns:
            dict, bytes, 또는 str: 응답 데이터
        """
    if params is None:
      params = self._build_params(**kwargs)

    for attempt in range(1, self.max_retries + 1):
      try:
        response = self.session.get(
          self.get_api_url(),
          params=params,
          timeout=self.timeout,
        )
        response.raise_for_status()

        if expect_json:
          return response.json()
        else:
          return response.content

      except requests.RequestException as e:
        logger.warning(f"OpenDart API 요청 실패 (시도 {attempt}/{self.max_retries}): {e}")
        if attempt < self.max_retries:
          wait_time = self.backoff_seconds**(attempt - 1)
          time.sleep(wait_time)
        else:
          logger.error(f"OpenDart API 요청 최종 실패 after {self.max_retries} attempts: {e}")
          raise

    raise requests.RequestException("OpenDart API 요청 최대 재시도 횟수 초과")

  def _validate_response(self, response: Dict[str, Any]) -> bool:
    """응답 유효성 검증

        Args:
            response: API 응답

        Returns:
            bool: 유효 여부
        """
    status = response.get("status")
    if status != "000":
      logger.warning(f"OpenDart API 응답 상태 오류: status={status}, message={response.get('message')}")
      return False
    return True

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
