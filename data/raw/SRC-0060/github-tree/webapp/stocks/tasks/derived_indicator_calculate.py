"""
Derived Indicator Calculation Task

파생지표 계산을 위한 Celery 태스크
"""
from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from stocks.models import Stock
from stocks.services.derived_indicator_service import (
  DerivedIndicatorService,
  calculate_derived_indicators_for_company,
)

from companies.models import Company

logger = logging.getLogger(__name__)


@shared_task(
  name="stocks.calculate_derived_indicators_for_stock",
  bind=True,
  max_retries=3,
  default_retry_delay=60,
)
def calculate_derived_indicators_for_stock(
  self,
  stock_id: int,
  fiscal_year: Optional[int] = None,
  fiscal_quarter: Optional[int] = None,
) -> dict:
  """특정 주식의 파생지표 계산

  Args:
    stock_id: Stock ID
    fiscal_year: 특정 연도만 계산 (None이면 전체)
    fiscal_quarter: 특정 분기만 계산 (None이면 전체)

  Returns:
    계산 결과 요약
  """
  try:
    stock = Stock.objects.select_related("company").get(id=stock_id)
    service = DerivedIndicatorService(stock)

    if fiscal_year and fiscal_quarter:
      # 특정 기간만 계산
      indicator = service.calculate_for_period(fiscal_year, fiscal_quarter)
      if indicator:
        return {
          "success": True,
          "stock_code": stock.code,
          "stock_name": stock.name,
          "calculated_count": 1,
          "periods": [f"{fiscal_year}Q{fiscal_quarter}"],
        }
      else:
        return {
          "success": False,
          "stock_code": stock.code,
          "stock_name": stock.name,
          "error": "재무제표 또는 주가 데이터를 찾을 수 없음",
        }
    else:
      # 모든 기간 계산
      indicators = service.calculate_all_available_periods()
      return {
        "success": True,
        "stock_code": stock.code,
        "stock_name": stock.name,
        "calculated_count": len(indicators),
        "periods": [f"{ind.fiscal_year}Q{ind.fiscal_quarter}" for ind in indicators],
      }

  except Stock.DoesNotExist:
    logger.error(f"Stock not found: {stock_id}")
    return {"success": False, "error": f"Stock ID {stock_id}를 찾을 수 없음"}
  except Exception as e:
    logger.exception(f"파생지표 계산 실패: {e}")
    raise self.retry(exc=e)


@shared_task(
  name="stocks.calculate_derived_indicators_for_company_task",
  bind=True,
  max_retries=3,
  default_retry_delay=60,
)
def calculate_derived_indicators_for_company_task(self, company_id: int) -> dict:
  """특정 회사의 모든 주식에 대해 파생지표 계산

  Args:
    company_id: Company ID

  Returns:
    계산 결과 요약
  """
  try:
    company = Company.objects.get(id=company_id)
    results = calculate_derived_indicators_for_company(company)

    total_count = sum(len(indicators) for indicators in results.values())

    return {
      "success": True,
      "company_name": company.name,
      "stock_count": len(results),
      "total_indicators": total_count,
      "stocks": {
        code: len(indicators)
        for code, indicators in results.items()
      },
    }

  except Company.DoesNotExist:
    logger.error(f"Company not found: {company_id}")
    return {"success": False, "error": f"Company ID {company_id}를 찾을 수 없음"}
  except Exception as e:
    logger.exception(f"회사 파생지표 계산 실패: {e}")
    raise self.retry(exc=e)


@shared_task(
  name="stocks.recalculate_derived_indicators_for_period",
  bind=True,
)
def recalculate_derived_indicators_for_period(self, fiscal_year: int, fiscal_quarter: int) -> dict:
  """특정 기간의 모든 주식에 대해 파생지표 재계산

  Args:
    fiscal_year: 회계연도
    fiscal_quarter: 분기

  Returns:
    계산 결과 요약
  """
  try:
    companies = (
      Company.objects.filter(
        financial_statements__fiscal_year=fiscal_year,
        financial_statements__fiscal_quarter=fiscal_quarter,
      ).distinct()
    )

    total_stocks = 0
    total_indicators = 0

    for company in companies:
      stocks = company.stocks.filter(is_listed=True)
      for stock in stocks:
        service = DerivedIndicatorService(stock)
        indicator = service.calculate_for_period(fiscal_year, fiscal_quarter)
        if indicator:
          total_indicators += 1
        total_stocks += 1

    return {
      "success": True,
      "fiscal_year": fiscal_year,
      "fiscal_quarter": fiscal_quarter,
      "companies_count": companies.count(),
      "stocks_processed": total_stocks,
      "indicators_calculated": total_indicators,
    }

  except Exception as e:
    logger.exception(f"기간별 파생지표 재계산 실패: {e}")
    raise self.retry(exc=e)
