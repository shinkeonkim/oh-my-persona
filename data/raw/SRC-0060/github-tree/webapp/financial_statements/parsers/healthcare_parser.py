"""
Healthcare Financial Statement Parser

TODO_parse.md의 헬스케어 계정 구조를 기반으로
재무제표 데이터를 JSON 구조로 파싱합니다.
"""
from __future__ import annotations

import copy
import logging
from typing import Dict

from .baseline_parser import BASELINE_ACCOUNTS, BaselineFinancialStatementParser

logger = logging.getLogger(__name__)

# 헬스케어 추가 계정 (Baseline 확장)
HEALTHCARE_ADDITIONAL_ACCOUNTS = {
  "BS": {
    "ifrs_IntangibleAssetsPatents": {
      "name": "특허/라이선스",
      "type": "postable",
    },
  },
  "IS": {
    "ifrs_ResearchAndDevelopmentExpense": {
      "name": "연구개발비",
      "type": "postable",
    },
    "ifrs_ClinicalTrialExpenses": {
      "name": "임상시험 비용",
      "type": "postable",
    },
  },
}


class HealthcareFinancialStatementParser(BaselineFinancialStatementParser):
  """헬스케어 재무제표 파서

  Baseline 계정 구조에 헬스케어 특화 계정을 추가한 파서입니다.
  """

  def __init__(self):
    """초기화"""
    super().__init__()
    # Baseline + Healthcare 계정 병합
    self.accounts = self._merge_healthcare_accounts()
    # 매핑 재구성
    self._account_id_to_path = self._build_account_id_to_path_mapping()

  def _merge_healthcare_accounts(self) -> Dict:
    """헬스케어 계정을 Baseline에 병합하여 새로운 딕셔너리 반환"""
    merged_accounts = copy.deepcopy(BASELINE_ACCOUNTS)

    for statement_type, accounts in HEALTHCARE_ADDITIONAL_ACCOUNTS.items():
      if statement_type not in merged_accounts:
        continue

      for account_id, account_info in accounts.items():
        # 기존 계정이 있으면 children만 추가
        if account_id in merged_accounts[statement_type]:
          if "children" in account_info and "children" in merged_accounts[statement_type][account_id]:
            merged_accounts[statement_type][account_id]["children"].update(account_info["children"])
        else:
          # 새로운 계정 추가
          merged_accounts[statement_type][account_id] = account_info

    return merged_accounts
