"""
IT/Communication Services Financial Statement Parser

TODO_parse.md의 IT/통신서비스 계정 구조를 기반으로
재무제표 데이터를 JSON 구조로 파싱합니다.
"""
from __future__ import annotations

import copy
import logging
from typing import Dict

from .baseline_parser import BASELINE_ACCOUNTS, BaselineFinancialStatementParser

logger = logging.getLogger(__name__)

# IT/통신서비스 추가 계정 (Baseline 확장)
IT_COMMUNICATION_ADDITIONAL_ACCOUNTS = {
  "BS": {
    "ifrs_IntangibleAssetsPatents": {
      "name": "특허권",
      "type": "postable",
    },
    "ifrs_IntangibleAssetsSoftware": {
      "name": "소프트웨어",
      "type": "postable",
    },
  },
  "IS": {
    "ifrs_ResearchAndDevelopmentExpense": {
      "name": "연구개발비",
      "type": "postable",
    },
  },
  "CF": {
    "ifrs_PaymentsToAcquireIntangibleAssets": {
      "name": "무형자산 취득",
      "type": "postable",
    },
  },
}


class ITCommunicationFinancialStatementParser(BaselineFinancialStatementParser):
  """IT/통신서비스 재무제표 파서

  Baseline 계정 구조에 IT/통신 특화 계정을 추가한 파서입니다.
  """

  def __init__(self):
    """초기화"""
    super().__init__()
    # Baseline + IT/Communication 계정 병합
    self.accounts = self._merge_it_communication_accounts()
    # 매핑 재구성
    self._account_id_to_path = self._build_account_id_to_path_mapping()

  def _merge_it_communication_accounts(self) -> Dict:
    """IT/통신서비스 계정을 Baseline에 병합하여 새로운 딕셔너리 반환"""
    merged_accounts = copy.deepcopy(BASELINE_ACCOUNTS)

    for statement_type, accounts in IT_COMMUNICATION_ADDITIONAL_ACCOUNTS.items():
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
