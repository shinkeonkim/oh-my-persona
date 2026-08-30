"""
Financial Statement Regeneration Service

Raw 데이터와 Mapping Rule을 기반으로 FinancialStatementItem과
FinancialStatementAccount를 재생성하는 서비스입니다.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional

from django.db import models, transaction

from financial_statements.models import (
  FinancialStatement,
  FinancialStatementAccount,
  FinancialStatementItem,
  FinancialStatementItemMappingRule,
  RawFinancialStatementItem,
)

from companies.models import Company

logger = logging.getLogger(__name__)


class FinancialStatementRegenerationService:
  """재무제표 재생성 서비스

  Raw 데이터와 Mapping Rule을 적용하여
  FinancialStatementItem과 FinancialStatementAccount를 재생성합니다.

  이 서비스는 idempotent하며, 여러 번 실행해도 동일한 결과를 생성합니다.
  """

  def __init__(self):
    """초기화"""
    self._mapping_cache: Dict[tuple, Optional[tuple]] = {}

  def regenerate_for_statement(self, statement: FinancialStatement) -> Dict[str, int]:
    """특정 재무제표에 대해 재생성

    Args:
      statement: 재생성할 재무제표

    Returns:
      생성/업데이트 통계
        - items_created: 생성된 항목 수
        - items_updated: 업데이트된 항목 수
        - accounts_created: 생성된 계정과목 수
    """
    logger.info(f"재무제표 재생성 시작: {statement}")

    with transaction.atomic():
      # 기존 FinancialStatementItem 삭제
      FinancialStatementItem.objects.filter(statement=statement).delete()

      # Mapping Rule 로드 (회사별 + 전체)
      self._load_mapping_rules(statement.company)

      # Raw 데이터 조회
      raw_items = RawFinancialStatementItem.objects.filter(statement=statement
                                                           ).select_related("account").order_by("order")

      items_created = 0
      accounts_created = 0
      accounts_cache: Dict[tuple, FinancialStatementAccount] = {}

      for raw_item in raw_items:
        # Mapping Rule 적용
        mapped_account_id, mapped_account_name = self._apply_mapping_rule(
          company=statement.company,
          source_account_id=raw_item.account.account_id,
          source_account_name=raw_item.account.account_name,
        )

        # FinancialStatementAccount 가져오기 또는 생성
        account_key = (mapped_account_id, mapped_account_name)
        if account_key not in accounts_cache:
          account, created = FinancialStatementAccount.objects.get_or_create(
            account_id=mapped_account_id,
            account_name=mapped_account_name,
            defaults={
              "account_category": raw_item.account.account_category,
              "category_name": raw_item.account.category_name,
              "account_detail": raw_item.account.account_detail,
            },
          )
          accounts_cache[account_key] = account
          if created:
            accounts_created += 1
        else:
          account = accounts_cache[account_key]

        # FinancialStatementItem 생성
        FinancialStatementItem.objects.create(
          statement=statement,
          account=account,
          current_amount=raw_item.current_amount,
          cumulative_amount=raw_item.cumulative_amount,
          order=raw_item.order,
          raw=raw_item.raw,
        )
        items_created += 1

    result = {
      "items_created": items_created,
      "items_updated": 0,  # 항상 새로 생성하므로 0
      "accounts_created": accounts_created,
    }

    logger.info(f"재무제표 재생성 완료: {statement} - "
                f"항목 {items_created}개 생성, 계정과목 {accounts_created}개 생성")

    return result

  def regenerate_for_company(
    self,
    company: Company,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
  ) -> Dict[str, int]:
    """특정 회사의 재무제표들에 대해 재생성

    Args:
      company: 대상 회사
      year: 회계연도 (None이면 전체)
      quarter: 분기 (None이면 전체)

    Returns:
      생성/업데이트 통계
        - statements_processed: 처리한 재무제표 수
        - total_items_created: 전체 생성된 항목 수
        - total_accounts_created: 전체 생성된 계정과목 수
    """
    logger.info(f"회사별 재무제표 재생성 시작: {company}, year={year}, quarter={quarter}")

    statements = FinancialStatement.objects.filter(company=company)

    if year is not None:
      statements = statements.filter(fiscal_year=year)
    if quarter is not None:
      statements = statements.filter(fiscal_quarter=quarter)

    statements_processed = 0
    total_items_created = 0
    total_accounts_created = 0

    for statement in statements:
      result = self.regenerate_for_statement(statement)
      statements_processed += 1
      total_items_created += result["items_created"]
      total_accounts_created += result["accounts_created"]

    result = {
      "statements_processed": statements_processed,
      "total_items_created": total_items_created,
      "total_accounts_created": total_accounts_created,
    }

    logger.info(
      f"회사별 재무제표 재생성 완료: {company} - "
      f"재무제표 {statements_processed}개, 항목 {total_items_created}개, 계정과목 {total_accounts_created}개"
    )

    return result

  def _load_mapping_rules(self, company: Company) -> None:
    """Mapping Rule 로드 및 캐싱"""
    # 전체 규칙 + 회사별 규칙 로드 (우선순위 순)
    rules = FinancialStatementItemMappingRule.objects.filter(
      is_active=True
    ).filter(models.Q(company__isnull=True)
             | models.Q(company=company)).select_related("company").order_by("-priority")

    # 캐시 초기화
    self._mapping_cache = {}

    # 규칙을 캐시에 저장 (우선순위가 높은 것이 나중에 저장되어 덮어씀)
    for rule in rules:
      key = (
        rule.company_id if rule.company else None,
        rule.source_account_id,
        rule.source_account_name,
      )
      value = (rule.target_account_id, rule.target_account_name)
      self._mapping_cache[key] = value

      logger.debug(
        f"Mapping Rule 로드: {rule.source_account_name} ({rule.source_account_id}) "
        f"-> {rule.target_account_name} ({rule.target_account_id})"
      )

  def _apply_mapping_rule(
    self,
    company: Company,
    source_account_id: str,
    source_account_name: str,
  ) -> tuple[str, str]:
    """Mapping Rule 적용

    Args:
      company: 대상 회사
      source_account_id: 원본 계정과목 ID
      source_account_name: 원본 계정과목명

    Returns:
      (mapped_account_id, mapped_account_name) 튜플
      매핑 규칙이 없으면 원본 그대로 반환
    """
    # 회사별 규칙 먼저 확인
    company_key = (company.id, source_account_id, source_account_name)
    if company_key in self._mapping_cache:
      return self._mapping_cache[company_key]

    # 전체 규칙 확인
    global_key = (None, source_account_id, source_account_name)
    if global_key in self._mapping_cache:
      return self._mapping_cache[global_key]

    # 매핑 규칙 없음 - 원본 그대로 반환
    return (source_account_id, source_account_name)
