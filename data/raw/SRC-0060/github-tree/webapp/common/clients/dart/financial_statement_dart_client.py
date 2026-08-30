"""
재무제표 조회 OpenDart Client
"""

import logging
from typing import Dict, List, Tuple

from .base_opendart_client import BaseOpenDartClient

logger = logging.getLogger(__name__)

# OpenDart API URL
DART_STATEMENT_URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

# 분기별 보고서 코드 매핑
QUARTER_TO_REPRT = {
  1: "11013",  # 1분기보고서
  2: "11012",  # 반기보고서
  3: "11014",  # 3분기보고서
  4: "11011",  # 사업보고서
}


class FinancialStatementDartClient(BaseOpenDartClient):
  """재무제표 조회 클라이언트

    OpenDart API를 통해 재무제표 데이터를 조회합니다.
    """

  def get_api_url(self) -> str:
    """API URL 반환

        Returns:
            str: 재무제표 API URL
        """
    return DART_STATEMENT_URL

  def fetch_financial_statement(
    self,
    corp_code: str,
    year: int,
    quarter: int,
    fs_div: str = "CFS",
    page_count: int = 100,
  ) -> Tuple[List[Dict[str, str]], bool]:
    """재무제표 조회

        Args:
            corp_code: 법인 코드 (8자리)
            year: 사업연도 (4자리)
            quarter: 분기 (1, 2, 3, 4)
            fs_div: 재무제표 구분 (CFS: 연결재무제표, OFS: 개별재무제표)
            page_count: 페이지당 건수 (최대 100)

        Returns:
            Tuple[List[Dict[str, str]], bool]: (재무제표 데이터 리스트, 성공 여부)
        """
    reprt_code = self._get_report_code(quarter)

    params = {
      "corp_code": corp_code,
      "bsns_year": str(year),
      "reprt_code": reprt_code,
      "fs_div": fs_div,
      "page_count": page_count,
    }

    try:
      response = self.fetch_data(params=self._build_params(**params), expect_json=True)

      # 응답 유효성 검증
      if not self._validate_response(response):
        return [], False

      # 데이터 추출
      result_list = response.get("list") or []
      logger.info(
        f"재무제표 조회 완료: corp_code={corp_code}, year={year}, quarter={quarter}, "
        f"fs_div={fs_div}, count={len(result_list)}"
      )
      return result_list, True

    except Exception as e:
      logger.error(
        f"재무제표 조회 실패: corp_code={corp_code}, year={year}, quarter={quarter}, "
        f"fs_div={fs_div}, error={e}"
      )
      return [], False

  @staticmethod
  def _get_report_code(quarter: int) -> str:
    """분기별 보고서 코드 반환

        Args:
            quarter: 분기 (1, 2, 3, 4)

        Returns:
            str: 보고서 코드

        Raises:
            ValueError: 지원하지 않는 분기
        """
    try:
      return QUARTER_TO_REPRT[quarter]
    except KeyError as exc:
      raise ValueError(f"Unsupported quarter: {quarter}") from exc
