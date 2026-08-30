"""
OpenDart 공시정보 > 고유번호 API 클라이언트
"""

import logging
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from typing import Dict

from .base_opendart_client import BaseOpenDartClient

logger = logging.getLogger(__name__)

DART_CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"


class CorpCodeDartClient(BaseOpenDartClient):
  """법인코드 조회 클라이언트

    OpenDart API를 통해 법인코드 정보를 조회합니다.
    """

  def get_api_url(self) -> str:
    """API URL 반환

        Returns:
            str: 법인코드 API URL
        """
    return DART_CORP_CODE_URL

  def fetch_corp_codes(self) -> Dict[str, Dict[str, str]]:
    """법인 코드 조회

    Returns:
        Dict[str, Dict[str, str]]: 종목 코드를 키로 하는 법인 정보 딕셔너리
            예: {"005930": {"corp_code": "00126380", "corp_name": "삼성전자"}}
    """
    try:
      # ZIP 파일 다운로드 (OpenDart는 XML을 ZIP으로 압축해서 제공)
      zip_content = self.fetch_data(expect_json=False)

      # ZIP 파일 압축 해제 및 XML 파싱
      corp_map: Dict[str, Dict[str, str]] = {}
      with zipfile.ZipFile(BytesIO(zip_content)) as archive:
        with archive.open("CORPCODE.xml") as corp_xml:
          tree = ET.parse(corp_xml)

      # XML 데이터 파싱
      for element in tree.findall(".//list"):
        stock_code = element.findtext("stock_code", default="").strip()
        corp_code = element.findtext("corp_code", default="").strip()
        corp_name = element.findtext("corp_name", default="").strip()
        corp_eng_name = element.findtext("corp_eng_name", default="").strip()

        # NOTE: 코드 정보가 없는 경우는 건너뛰어 처리한다.
        # - 수집되지 않는 회사 정보가 있을 수 있음
        if not stock_code or not corp_code:
          continue

        corp_map[self._parse_stock_code(stock_code)] = {
          "corp_code": corp_code,
          "corp_name": corp_name,
          "corp_eng_name": corp_eng_name or None,
        }

      logger.info(f"법인코드 조회 완료: {len(corp_map)}개")
      return corp_map

    except Exception as e:
      logger.error(f"법인코드 조회 실패: {e}")
      return {}

  @staticmethod
  def _parse_stock_code(value: str) -> str:
    """종목 코드 파싱 (6자리로 패딩)

    Args:
        value: 종목 코드

    Returns:
        str: 파싱된 종목 코드 (6자리)
    """
    return value.strip().zfill(6)
