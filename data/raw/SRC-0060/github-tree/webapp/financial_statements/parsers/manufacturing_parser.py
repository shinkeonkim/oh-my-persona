"""
Manufacturing Financial Statement Parser

TODO_parse.md의 제조업(Manufacturing) 계정 구조를 기반으로
재무제표 데이터를 JSON 구조로 파싱합니다.
"""
from __future__ import annotations

import copy
import logging
from typing import Dict

from .baseline_parser import BASELINE_ACCOUNTS, BaselineFinancialStatementParser

logger = logging.getLogger(__name__)

# 제조업 추가 계정 (Baseline 확장)
MANUFACTURING_ADDITIONAL_ACCOUNTS = {
  "BS": {
    "ifrs_Inventories": {
      "name": "재고자산",
      "type": "abstract",
      "children": {
        "ifrs_InventoriesRawMaterials": {
          "name": "원재료",
          "type": "postable"
        },
        "ifrs_InventoriesWorkInProgress": {
          "name": "재공품",
          "type": "postable"
        },
        "ifrs_InventoriesFinishedGoods": {
          "name": "완제품",
          "type": "postable"
        },
      },
    },
    "ifrs_CurrentPortionOfNoncurrentBorrowings": {
      "name": "유동성장기부채",
      "type": "postable",
    },
    "ifrs_EquityOwners": {
      "name": "자본(지배주주지분)",
      "type": "postable",
    },
  },
  "IS": {
    "ifrs_NetIncomeOwners": {
      "name": "당기순이익(지배주주)",
      "type": "postable",
    },
  },
  "CF": {
    "ifrs_IncreaseDecreaseInInventories": {
      "name": "재고자산 증감",
      "type": "postable",
    },
  },
}


class ManufacturingFinancialStatementParser(BaselineFinancialStatementParser):
  """제조업 재무제표 파서

  Baseline 계정 구조에 제조업 특화 계정을 추가한 파서입니다.
  """

  def __init__(self):
    """초기화"""
    super().__init__()
    # Baseline + Manufacturing 계정 병합
    self.accounts = self._merge_manufacturing_accounts()
    # 매핑 재구성
    self._account_id_to_path = self._build_account_id_to_path_mapping()

  def _merge_manufacturing_accounts(self) -> Dict:
    """제조업 계정을 Baseline에 병합하여 새로운 딕셔너리 반환"""
    merged_accounts = copy.deepcopy(BASELINE_ACCOUNTS)

    for statement_type, accounts in MANUFACTURING_ADDITIONAL_ACCOUNTS.items():
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
