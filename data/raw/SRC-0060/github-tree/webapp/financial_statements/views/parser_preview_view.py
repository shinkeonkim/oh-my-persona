"""
Parser Preview View

재무제표에 특정 파서를 적용했을 때의 미리보기를 제공합니다.
"""
import importlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from financial_statements.models import FinancialStatement
from unfold.views import UnfoldModelAdminViewMixin

logger = logging.getLogger(__name__)


class ParserPreviewView(UnfoldModelAdminViewMixin, TemplateView):
  """파서 미리보기 커스텀 페이지"""

  title = _("Parser Preview")
  permission_required = ()
  template_name = "admin/financial_statements/financialstatement/parser_preview.html"

  def get_available_parsers(self) -> List[Dict[str, str]]:
    """사용 가능한 파서 목록 가져오기"""
    # __file__을 사용하여 현재 파일 기준으로 parsers 디렉토리 찾기
    current_file = Path(__file__)
    parsers_dir = current_file.parent.parent / "parsers"

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
          0, {
            "module": module_name,
            "class": class_name,
            "name": file_path.stem,
            "display_name": display_name,
          }
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

  def get_context_data(self, **kwargs):
    """컨텍스트 데이터 추가"""
    context = super().get_context_data(**kwargs)
    context["opts"] = self.model_admin.model._meta

    # 선택된 재무제표 ID
    statement_id = self.request.GET.get("statement_id")
    parser_name = self.request.GET.get("parser")

    # 사용 가능한 파서 목록
    context["parsers"] = self.get_available_parsers()
    context["selected_parser"] = parser_name

    if statement_id:
      try:
        statement = FinancialStatement.objects.get(pk=statement_id)
        context["statement"] = statement

        if parser_name:
          # 파서 적용 및 미리보기
          parser_info = next((p for p in context["parsers"] if p["name"] == parser_name), None)
          if parser_info:
            context["preview_result"] = self._generate_preview(statement, parser_info)
      except FinancialStatement.DoesNotExist:
        messages.error(self.request, _("재무제표를 찾을 수 없습니다."))

    return context

  def _generate_preview(self, statement: FinancialStatement, parser_info: Dict) -> Dict[str, Any]:
    """파서 적용 및 미리보기 데이터 생성"""
    try:
      # 파서 동적 로드
      module = importlib.import_module(parser_info["module"])
      ParserClass = getattr(module, parser_info["class"])
      parser = ParserClass()

      # 파싱 실행
      parsed_data = parser.parse(statement)

      # 누락 키 감지
      missing_keys = self._detect_missing_keys(parsed_data, parser)

      # JSON 미리보기
      json_preview = json.dumps(parsed_data, ensure_ascii=False, indent=2)

      # 각 키별 값 정보
      key_values = self._extract_key_values(parsed_data)

      return {
        "success": True,
        "parsed_data": parsed_data,
        "json_preview": json_preview,
        "missing_keys": missing_keys,
        "key_values": key_values,
        "parser_name": parser_info["display_name"],
      }
    except Exception as e:
      logger.exception(f"파서 적용 실패: {e}")
      return {
        "success": False,
        "error": str(e),
        "parser_name": parser_info["display_name"],
      }

  def _detect_missing_keys(self, parsed_data: Dict, parser) -> List[Dict[str, str]]:
    """누락된 키 감지 (Abstract/Postable 모두 포함)"""
    missing = []

    # 파서가 정의한 모든 account_id를 재귀적으로 추출
    expected_keys = {}  # {account_id: {"name": ..., "type": ..., "statement_type": ...}}
    if hasattr(parser, "accounts"):
      for statement_type, accounts in parser.accounts.items():
        self._collect_expected_keys(accounts, statement_type, expected_keys)

    # 실제 파싱된 데이터에서 찾은 키 (값이 있는 키만)
    found_keys = set()
    for statement_type in ["BS", "IS", "CF"]:
      if statement_type in parsed_data:
        found_keys.update(self._collect_account_ids_with_values(parsed_data[statement_type]))

    # 누락된 키 (파서에 정의되어 있지만 실제 데이터에 없는 키)
    missing_keys = set(expected_keys.keys()) - found_keys

    for key in sorted(missing_keys):
      info = expected_keys[key]
      missing.append(
        {
          "account_id": key,
          "account_name": info["name"],
          "account_type": info["type"],
          "statement_type": info["statement_type"],
        }
      )

    return missing

  def _collect_expected_keys(
    self,
    account_structure: Dict,
    statement_type: str,
    result: Dict,
  ) -> None:
    """파서 정의에서 모든 예상 키를 재귀적으로 수집"""
    for account_id, account_info in account_structure.items():
      if isinstance(account_info, dict):
        result[account_id] = {
          "name": account_info.get("name", account_id),
          "type": account_info.get("type", "postable"),
          "statement_type": statement_type,
        }

        # Children이 있으면 재귀
        if "children" in account_info:
          self._collect_expected_keys(account_info["children"], statement_type, result)

  def _collect_account_ids_with_values(self, data: Any) -> set:
    """재귀적으로 실제 데이터가 있는 account_id만 수집"""
    keys = set()
    if isinstance(data, dict):
      # account_id가 있는 노드
      if "account_id" in data:
        account_id = data["account_id"]
        # 값이 있거나, items가 있으면 (즉, 파싱된 데이터에 존재하면) 추가
        keys.add(account_id)

        # items가 있으면 재귀
        if "items" in data and isinstance(data["items"], list):
          for item in data["items"]:
            keys.update(self._collect_account_ids_with_values(item))
      else:
        # 일반 딕셔너리
        for value in data.values():
          keys.update(self._collect_account_ids_with_values(value))
    elif isinstance(data, list):
      for item in data:
        keys.update(self._collect_account_ids_with_values(item))
    return keys

  def _find_account_name(self, account_id: str, parser) -> str:
    """account_id에 해당하는 이름 찾기"""
    if hasattr(parser, "accounts"):
      for statement_type, accounts in parser.accounts.items():
        if account_id in accounts:
          return accounts[account_id].get("name", "")
    return ""

  def _find_statement_type(self, account_id: str, parser) -> str:
    """account_id가 속한 statement_type 찾기"""
    if hasattr(parser, "accounts"):
      for statement_type, accounts in parser.accounts.items():
        if account_id in accounts:
          return statement_type
    return ""

  def _extract_key_values(self, data: Dict) -> List[Dict[str, Any]]:
    """각 키별 값 정보 추출 (새로운 계층 구조)"""
    key_values = []

    for statement_type in ["BS", "IS", "CF"]:
      if statement_type in data:
        self._extract_values_recursive(data[statement_type], statement_type, key_values, [])

    return key_values

  def _extract_values_recursive(self, data: Any, statement_type: str, result: List, path: List[str]):
    """재귀적으로 값 추출 (계층 구조)"""
    if isinstance(data, dict):
      # 계정 노드인 경우
      if "account_id" in data:
        print(data)
        account_id = data.get("account_id")
        account_name = data.get("account_name")
        account_type = data.get("type", "unknown")
        value = data.get("value")

        # 값이 있으면 추가 (Abstract든 Postable이든)
        if value is not None:
          result.append(
            {
              "statement_type": statement_type,
              "account_id": account_id,
              "account_name": account_name,
              "account_type": account_type,
              "value": value,
              "path": " > ".join(path + [account_name]) if path else account_name,
            }
          )

        # items가 있으면 재귀
        if "items" in data and isinstance(data["items"], list):
          new_path = path + [account_name]
          for item in data["items"]:
            self._extract_values_recursive(item, statement_type, result, new_path)

      # 일반 딕셔너리인 경우 (최상위 레벨)
      else:
        for key, value in data.items():
          self._extract_values_recursive(value, statement_type, result, path)

    elif isinstance(data, list):
      for item in data:
        self._extract_values_recursive(item, statement_type, result, path)
