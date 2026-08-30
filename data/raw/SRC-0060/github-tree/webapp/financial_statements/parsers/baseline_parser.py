"""
Baseline Financial Statement Parser

TODO_parse.md의 Baseline 계정 구조를 기반으로
재무제표 데이터를 JSON 구조로 파싱합니다.
"""
from __future__ import annotations

import logging
from typing import Dict, List

from financial_statements.models import (
  FinancialStatement,
  FinancialStatementItem,
)

logger = logging.getLogger(__name__)

BASELINE_ACCOUNTS = {
  # Balance Sheet
  "BS": {
    "ifrs-full_Assets": {
      "name": "자산",
      "type": "abstract",
      "children": {
        "ifrs-full_CurrentAssets": {
          "name": "유동자산",
          "type": "abstract",
          "children": {
            "ifrs-full_CashAndCashEquivalents": {
              "name": "현금및현금성자산",
              "type": "postable"
            },
            "ifrs_CurrentFinancialAssets": {
              "name": "단기금융자산",
              "type": "postable"
            },
            "ifrs_TradeReceivables": {
              "name": "매출채권",
              "type": "postable"
            },
            "ifrs-full_Inventories": {
              "name": "재고자산",
              "type": "postable"
            },
          },
        },
        "ifrs-full_NoncurrentAssets": {
          "name": "비유동자산",
          "type": "abstract",
          "children": {
            "ifrs_NoncurrentFinancialAssets": {
              "name": "장기금융자산",
              "type": "postable"
            },
            "ifrs_PropertyPlantEquipment": {
              "name": "유형자산",
              "type": "postable"
            },
            "ifrs_IntangibleAssets": {
              "name": "무형자산",
              "type": "postable"
            },
            "ifrs_InvestmentProperty": {
              "name": "투자부동산",
              "type": "postable"
            },
          },
        },
      },
    },
    "ifrs-full_Liabilities": {
      "name": "부채",
      "type": "abstract",
      "children": {
        "	ifrs-full_CurrentLiabilities": {
          "name": "유동부채",
          "type": "abstract",
          "children": {
            "ifrs-full_ShorttermBorrowings": {
              "name": "단기차입금",
              "type": "postable"
            },
            "ifrs_TradePayables": {
              "name": "매입채무",
              "type": "postable"
            },
            "ifrs_ProvisionsCurrent": {
              "name": "단기충당부채",
              "type": "postable"
            },
          },
        },
        "ifrs-full_NoncurrentLiabilities": {
          "name": "비유동부채",
          "type": "abstract",
          "children": {
            "ifrs-full_LongtermBorrowings": {
              "name": "장기차입금",
              "type": "postable"
            },
            "ifrs-full_NoncurrentProvisions": {
              "name": "장기충당부채",
              "type": "postable"
            },
          },
        },
      },
    },
    "ifrs-full_Equity": {
      "name": "자본",
      "type": "abstract",
      "children": {
        "ifrs-full_IssuedCapital": {
          "name": "자본금",
          "type": "postable"
        },
        "ifrs-full_SharePremium": {
          "name": "자본잉여금",
          "type": "postable"
        },
        "ifrs-full_RetainedEarnings": {
          "name": "이익잉여금",
          "type": "postable"
        },
        "ifrs_OtherComponentsOfEquity": {
          "name": "기타자본항목",
          "type": "postable"
        },
      },
    },
  },
  # Income Statement
  "IS": {
    "ifrs-full_Revenue": {
      "name": "매출액",
      "type": "postable"
    },
    "ifrs_Expenses": {
      "name": "비용",
      "type": "abstract",
      "children": {
        "ifrs_CostOfGoodsSold": {
          "name": "매출원가",
          "type": "postable"
        },
        "ifrs_SellingGeneralAdministrativeExpenses": {
          "name": "판매비와관리비",
          "type": "postable",
          "children": {
            "ifrs_EmployeeBenefitsExpense": {
              "name": "인건비",
              "type": "postable"
            },
            "ifrs_DepreciationAmortization": {
              "name": "감가상각비",
              "type": "postable"
            },
          },
        },
      },
    },
    "ifrs_OperatingIncome": {
      "name": "영업이익",
      "type": "postable"
    },
    "ifrs_FinanceIncome": {
      "name": "금융수익",
      "type": "postable"
    },
    "ifrs_FinanceCosts": {
      "name": "금융비용",
      "type": "postable"
    },
    "ifrs_ProfitBeforeTax": {
      "name": "법인세비용차감전순이익",
      "type": "postable"
    },
    "ifrs_IncomeTaxExpense": {
      "name": "법인세비용",
      "type": "postable"
    },
    "ifrs_NetIncome": {
      "name": "당기순이익",
      "type": "postable"
    },
  },
  # Cash Flow
  "CF": {
    "ifrs_CashFlowsFromOperatingActivities": {
      "name": "영업활동현금흐름",
      "type": "abstract",
      "children": {
        "ifrs_CF_Adjustments": {
          "name": "조정항목",
          "type": "abstract",
          "children": {
            "ifrs_DepreciationAmortisationCF": {
              "name": "감가상각 및 상각",
              "type": "postable"
            },
            "ifrs_InterestPaid": {
              "name": "이자지급액",
              "type": "postable"
            },
          },
        },
        "ifrs_IncreaseDecreaseInTradeReceivables": {
          "name": "매출채권 증감",
          "type": "postable"
        },
        "ifrs_CashFlowsFromOperatingActivities_Total": {
          "name": "영업활동현금흐름 합계",
          "type": "postable",
        },
      },
    },
    "ifrs_CashFlowsFromInvestingActivities": {
      "name": "투자활동현금흐름",
      "type": "abstract",
      "children": {
        "ifrs_CapexPaymentsToAcquirePPE": {
          "name": "유형자산 취득",
          "type": "postable"
        },
      },
    },
    "ifrs_CashFlowsFromFinancingActivities": {
      "name": "재무활동현금흐름",
      "type": "abstract",
      "children": {
        "ifrs_RepaymentsOfBorrowings": {
          "name": "차입금 상환",
          "type": "postable"
        },
        "ifrs-full_DividendsPaid": {
          "name": "배당금 지급",
          "type": "postable"
        },
      },
    },
  },
}


class BaselineFinancialStatementParser:
  """Baseline 재무제표 파서

  Baseline 계정 구조를 기반으로 재무제표 데이터를 파싱하여
  JSON 구조로 변환합니다.
  """

  def __init__(self):
    """초기화"""
    self._account_id_to_path = self._build_account_id_to_path_mapping()

  def parse(self, statement: FinancialStatement) -> Dict:
    """재무제표 파싱

    Args:
      statement: 파싱할 재무제표

    Returns:
      Baseline 구조로 변환된 JSON
      {
        "BS": { ... },
        "IS": { ... },
        "CF": { ... },
        "meta": {
          "company": "...",
          "year": 2024,
          "quarter": 4,
          ...
        }
      }
    """
    logger.info(f"재무제표 파싱 시작: {statement}")

    # FinancialStatementItem 조회
    items = FinancialStatementItem.objects.filter(statement=statement).select_related("account")

    # Statement type별로 분류
    bs_items = []
    is_items = []
    cf_items = []

    for item in items:
      category = item.account.account_category
      if category == "BS":
        bs_items.append(item)
      elif category in ("IS", "CIS"):
        is_items.append(item)
      elif category == "CF":
        cf_items.append(item)

    # Baseline 구조로 변환
    result = {
      "BS": self._parse_statement_type(bs_items, "BS"),
      "IS": self._parse_statement_type(is_items, "IS"),
      "CF": self._parse_statement_type(cf_items, "CF"),
      "meta": {
        "company": statement.company.name,
        "company_id": statement.company.id,
        "corp_code": statement.company.corp_code,
        "year": statement.fiscal_year,
        "quarter": statement.fiscal_quarter,
        "report_type": statement.report_type,
        "source": statement.source,
        "is_consolidated": statement.is_consolidated,
        "currency": statement.currency,
        "submission_date": statement.submission_date.isoformat() if statement.submission_date else None,
      },
    }

    logger.info(f"재무제표 파싱 완료: {statement}")

    return result

  def _parse_statement_type(
    self,
    items: List[FinancialStatementItem],
    statement_type: str,
  ) -> Dict:
    """특정 statement type의 항목들을 파싱

    Args:
      items: 항목 리스트
      statement_type: BS, IS, CF

    Returns:
      Baseline 계층 구조로 변환된 딕셔너리
    """
    # 항목을 account_id로 매핑
    items_by_account = {}
    for item in items:
      items_by_account[item.account.account_id] = item

    # Baseline 계정 구조가 있는지 확인
    if not hasattr(self, 'accounts'):
      self.accounts = BASELINE_ACCOUNTS

    # 계층 구조 빌드
    if statement_type in self.accounts:
      result = self._build_hierarchy(self.accounts[statement_type], items_by_account)
    else:
      result = {}

    # Baseline에 없는 계정들을 "other"에 추가
    mapped_account_ids = set(self._account_id_to_path.keys())
    unmapped_items = [item for item in items if item.account.account_id not in mapped_account_ids]

    if unmapped_items:
      result["other"] = {
        "account_id":
        "other",
        "account_name":
        "기타 항목",
        "items": [
          {
            "account_id": item.account.account_id,
            "account_name": item.account.account_name,
            "value": float(item.current_amount) if item.current_amount else None,
            "cumulative_value": float(item.cumulative_amount) if item.cumulative_amount else None,
            "order": item.order,
          } for item in unmapped_items
        ]
      }

    return result

  def _build_hierarchy(
    self,
    account_structure: Dict,
    items_by_account: Dict[str, FinancialStatementItem],
  ) -> Dict:
    """계층 구조 빌드

    Args:
      account_structure: 계정 구조 정의 (BASELINE_ACCOUNTS의 일부)
      items_by_account: account_id -> FinancialStatementItem 매핑

    Returns:
      계층 구조 딕셔너리
    """
    result = {}

    for account_id, account_info in account_structure.items():
      if not isinstance(account_info, dict):
        continue

      account_type = account_info.get("type", "postable")
      account_name = account_info.get("name", account_id)

      # 노드 기본 구조
      node = {
        "account_id": account_id,
        "account_name": account_name,
        "type": account_type,
      }

      # 데이터가 있으면 값 추가 (Abstract든 Postable이든)
      if account_id in items_by_account:
        item = items_by_account[account_id]
        node["value"] = float(item.current_amount) if item.current_amount else None
        node["cumulative_value"] = float(item.cumulative_amount) if item.cumulative_amount else None
        node["order"] = item.order

      # Children이 있으면 재귀적으로 처리
      if "children" in account_info:
        child_result = self._build_hierarchy(account_info["children"], items_by_account)
        if child_result:
          node["items"] = list(child_result.values())

      # Abstract 노드는 항상 추가, Postable은 데이터가 있을 때만 추가
      if account_type == "abstract":
        result[account_id] = node
      elif account_id in items_by_account:
        result[account_id] = node

    return result

  def _build_account_id_to_path_mapping(self) -> Dict[str, List[str]]:
    """계정 ID -> 경로 매핑 빌드

    Returns:
      {account_id: [path, components]}
      예: {"ifrs_CashAndCashEquivalents": ["Assets", "CurrentAssets", "CashAndCashEquivalents"]}
    """
    mapping = {}

    for statement_type, accounts in BASELINE_ACCOUNTS.items():
      self._build_mapping_recursive(accounts, [], mapping)

    return mapping

  def _build_mapping_recursive(
    self,
    node: Dict,
    path: List[str],
    mapping: Dict[str, List[str]],
  ) -> None:
    """재귀적으로 계정 ID -> 경로 매핑 빌드"""
    for account_id, account_info in node.items():
      if isinstance(account_info, dict):
        current_path = path + [account_id]
        mapping[account_id] = current_path

        # children이 있으면 재귀
        if "children" in account_info:
          self._build_mapping_recursive(account_info["children"], current_path, mapping)
