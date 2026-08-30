import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List

from django.shortcuts import get_object_or_404

from financial_statements.models import FinancialStatement
from rest_framework import generics, status
from rest_framework.response import Response

from companies.models import Company

logger = logging.getLogger(__name__)

# 섹터별 기본 파서 매핑
SECTOR_PARSER_MAPPING = {
  # 제조업 관련
  "제조": "manufacturing_parser",
  "기계·장비": "manufacturing_parser",
  "운송장비·부품": "manufacturing_parser",
  "비금속": "manufacturing_parser",
  "기타제조": "manufacturing_parser",
  # 금속 관련
  "금속": "manufacturing_parser",
  # IT/통신 관련
  "통신": "it_communication_parser",
  "전기·전자": "it_communication_parser",
  "IT 서비스": "it_communication_parser",
  "출판·매체복제": "it_communication_parser",
  # 에너지/유틸리티 관련
  "전기·가스": "energy_utilities_parser",
  "전기·가스·수도": "energy_utilities_parser",
  # 헬스케어 관련
  "제약": "healthcare_parser",
  "의료·정밀기기": "healthcare_parser",
  # 소비재 관련
  "유통": "consumer_parser",
  "음식료·담배": "consumer_parser",
  "섬유·의류": "consumer_parser",
  "일반서비스": "consumer_parser",
  "오락·문화": "consumer_parser",
  # 화학
  "화학": "manufacturing_parser",
  # 건설
  "건설": "manufacturing_parser",
  # 종이/목재
  "종이·목재": "manufacturing_parser",
  # 운송
  "운송·창고": "consumer_parser",
  # 금융 관련 - baseline 사용
  "금융": "baseline_parser",
  "보험": "baseline_parser",
  "은행": "baseline_parser",
  "증권": "baseline_parser",
  "기타금융": "baseline_parser",
  # 부동산
  "부동산": "baseline_parser",
  # 농업
  "농업, 임업 및 어업": "baseline_parser",
  # 기타
  "기타": "baseline_parser",
}


class CompanyFinancialStatementDetailAPIView(generics.RetrieveAPIView):
  """
  GET /api/v1/companies/:corp_code/financial_statements/:id/

  특정 재무제표를 파서로 파싱한 JSON 결과를 반환합니다.

  Query Parameters:
  - parser: 사용할 파서 이름 (기본값: baseline_parser)
    - baseline_parser: Baseline (기본형)
    - manufacturing_parser: Manufacturing (제조업)
    - it_communication_parser: IT/Communication (IT/통신)
    - energy_utilities_parser: Energy/Utilities (에너지/유틸리티)
    - healthcare_parser: Healthcare (헬스케어)
    - consumer_parser: Consumer (소비재)
  """

  def get(self, request, **kwargs):
    corp_code = self.kwargs["corp_code"]
    statement_id = self.kwargs["pk"]

    # 회사 조회 (섹터 정보 포함)
    company = get_object_or_404(Company.objects.select_related("sector"), corp_code=corp_code)

    # 재무제표 조회
    statement = get_object_or_404(
      FinancialStatement,
      pk=statement_id,
      company=company,
    )

    # 파서 선택: query parameter가 있으면 사용, 없으면 섹터 기반 기본값 사용
    parser_name = request.query_params.get("parser")
    if not parser_name:
      parser_name = self._get_default_parser_for_company(company)

    # 파서 정보 조회
    parser_info = self._get_parser_info(parser_name)
    if not parser_info:
      return Response(
        {"error": f"Invalid parser: {parser_name}"},
        status=status.HTTP_400_BAD_REQUEST,
      )

    # 파싱 실행
    try:
      parsed_data = self._parse_with_parser(statement, parser_info)
      return Response(parsed_data)
    except Exception as e:
      logger.exception(f"파서 적용 실패: {e}")
      return Response(
        {"error": f"Failed to parse financial statement: {str(e)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
      )

  def _get_available_parsers(self) -> List[Dict[str, str]]:
    """사용 가능한 파서 목록 가져오기"""
    # financial_statements/parsers 디렉토리 찾기
    from financial_statements import parsers as parsers_module

    parsers_dir = Path(parsers_module.__file__).parent

    logger.info(f"Looking for parsers in: {parsers_dir}")

    parsers = []

    if not parsers_dir.exists():
      logger.warning(f"Parsers directory does not exist: {parsers_dir}")
      return parsers

    for file_path in parsers_dir.glob("*_parser.py"):
      logger.info(f"Found parser file: {file_path.name}")

      if file_path.stem == "baseline_parser":
        # Baseline을 맨 앞에
        module_name = f"financial_statements.parsers.{file_path.stem}"
        class_name = "BaselineFinancialStatementParser"
        display_name = "Baseline (기본형)"
        parsers.insert(
          0,
          {
            "module": module_name,
            "class": class_name,
            "name": file_path.stem,
            "display_name": display_name,
          },
        )
      elif file_path.stem != "__init__":
        # 파서별 클래스명 매핑
        class_name_map = {
          "manufacturing_parser": "ManufacturingFinancialStatementParser",
          "it_communication_parser": "ITCommunicationFinancialStatementParser",
          "energy_utilities_parser": "EnergyUtilitiesFinancialStatementParser",
          "healthcare_parser": "HealthcareFinancialStatementParser",
          "consumer_parser": "ConsumerFinancialStatementParser",
        }

        # 디스플레이 이름
        display_name_map = {
          "manufacturing_parser": "Manufacturing (제조업)",
          "it_communication_parser": "IT/Communication (IT/통신)",
          "energy_utilities_parser": "Energy/Utilities (에너지/유틸리티)",
          "healthcare_parser": "Healthcare (헬스케어)",
          "consumer_parser": "Consumer (소비재)",
        }

        class_name = class_name_map.get(file_path.stem, "UnknownParser")
        display_name = display_name_map.get(file_path.stem, file_path.stem)

        module_name = f"financial_statements.parsers.{file_path.stem}"
        parsers.append(
          {
            "module": module_name,
            "class": class_name,
            "name": file_path.stem,
            "display_name": display_name,
          }
        )

    logger.info(f"Found {len(parsers)} parsers: {[p['display_name'] for p in parsers]}")
    return parsers

  def _get_default_parser_for_company(self, company: Company) -> str:
    """회사의 섹터에 따라 기본 파서 결정"""
    if company.sector:
      sector_name = company.sector.name
      default_parser = SECTOR_PARSER_MAPPING.get(sector_name, "baseline_parser")
      logger.info(f"Company {company.name} sector: {sector_name}, using parser: {default_parser}")
      return default_parser

    logger.info(f"Company {company.name} has no sector, using baseline_parser")
    return "baseline_parser"

  def _get_parser_info(self, parser_name: str) -> Dict[str, str] | None:
    """파서 정보 조회"""
    parsers = self._get_available_parsers()
    return next((p for p in parsers if p["name"] == parser_name), None)

  def _parse_with_parser(self, statement: FinancialStatement, parser_info: Dict) -> Dict[str, Any]:
    """파서로 재무제표 파싱"""
    # 파서 동적 로드
    module = importlib.import_module(parser_info["module"])
    ParserClass = getattr(module, parser_info["class"])
    parser = ParserClass()

    # 파싱 실행
    parsed_data = parser.parse(statement)

    return {
      "id": statement.id,
      "company_name": statement.company.name,
      "corp_code": statement.company.corp_code,
      "fiscal_year": statement.fiscal_year,
      "fiscal_quarter": statement.fiscal_quarter,
      "report_type": statement.report_type,
      "report_type_display": statement.get_report_type_display(),
      "currency": statement.currency,
      "is_consolidated": statement.is_consolidated,
      "submission_date": statement.submission_date,
      "receipt_no": statement.receipt_no,
      "source": statement.source,
      "source_display": statement.get_source_display(),
      "parser": parser_info["display_name"],
      "data": parsed_data,
    }
