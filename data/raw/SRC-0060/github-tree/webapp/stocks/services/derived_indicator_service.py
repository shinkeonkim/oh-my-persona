"""
Derived Indicator Service

재무제표와 주가 데이터를 기반으로 파생지표를 계산하는 서비스
"""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Optional

from financial_statements.models import FinancialStatement, FinancialStatementItem
from stocks.models import DerivedIndicator, Stock, StockPrice

from companies.models import Company

logger = logging.getLogger(__name__)


class DerivedIndicatorService:
  """파생지표 계산 서비스"""

  def __init__(self, stock: Stock):
    self.stock = stock
    self.company = stock.company

  def calculate_for_period(
    self,
    fiscal_year: int,
    fiscal_quarter: int,
    reference_date: Optional[date] = None,
  ) -> Optional[DerivedIndicator]:
    """특정 기간의 파생지표를 계산합니다.

    Args:
      fiscal_year: 회계연도
      fiscal_quarter: 분기 (1, 2, 3, 4)
      reference_date: 기준일 (None이면 분기 말일 주가 사용)

    Returns:
      계산된 DerivedIndicator 객체 또는 None
    """
    logger.info(f"파생지표 계산 시작: {self.stock.name} {fiscal_year}Q{fiscal_quarter}")

    # 재무제표 조회
    financial_statement = self._get_financial_statement(fiscal_year, fiscal_quarter)
    if not financial_statement:
      logger.warning(f"재무제표를 찾을 수 없음: {self.company.name} {fiscal_year}Q{fiscal_quarter}")
      return None

    # 재무제표에서 주요 수치 추출
    financial_data = self._extract_financial_data(financial_statement)

    # 기준일 주가 조회
    stock_price = self._get_reference_stock_price(fiscal_year, fiscal_quarter, reference_date)
    if not stock_price:
      logger.warning(f"기준일 주가를 찾을 수 없음: {self.stock.name} {fiscal_year}Q{fiscal_quarter}")
      # 주가 없어도 재무제표 기반 지표는 계산 가능하므로 계속 진행
      reference_price = None
      reference_date_actual = None
      market_cap = None
      total_shares = None
    else:
      reference_price = stock_price.close_price
      reference_date_actual = stock_price.trade_date
      market_cap = stock_price.market_cap
      total_shares = stock_price.shares

    # 파생지표 계산
    indicators = self._calculate_indicators(
      financial_data=financial_data,
      reference_price=reference_price,
      total_shares=total_shares,
      fiscal_quarter=fiscal_quarter,
    )

    # financial_data에서 모델 필드가 아닌 항목 제거
    financial_data_for_model = {
      "net_income": financial_data.get("net_income"),
      "total_equity": financial_data.get("total_equity"),
      "total_assets": financial_data.get("total_assets"),
      "calculation_notes": financial_data.get("calculation_notes", {}),
    }

    # DerivedIndicator 생성 또는 업데이트
    derived_indicator, created = DerivedIndicator.objects.update_or_create(
      stock=self.stock,
      company=self.company,
      fiscal_year=fiscal_year,
      fiscal_quarter=fiscal_quarter,
      defaults={
        "financial_statement": financial_statement,
        "reference_price": reference_price,
        "reference_date": reference_date_actual,
        "market_cap": market_cap,
        "total_shares": total_shares,
        **indicators,
        **financial_data_for_model,
      },
    )

    action = "생성" if created else "업데이트"
    logger.info(f"파생지표 {action} 완료: {self.stock.name} {fiscal_year}Q{fiscal_quarter}")

    return derived_indicator

  def _get_financial_statement(self, fiscal_year: int, fiscal_quarter: int) -> Optional[FinancialStatement]:
    """재무제표 조회 (연결 우선, 없으면 개별)"""
    # 연결재무제표 우선
    statement = (
      FinancialStatement.objects.filter(
        company=self.company,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        source="CFS",
      ).order_by("-created_at").first()
    )

    # 연결재무제표 없으면 개별재무제표
    if not statement:
      statement = (
        FinancialStatement.objects.filter(
          company=self.company,
          fiscal_year=fiscal_year,
          fiscal_quarter=fiscal_quarter,
          source="OFS",
        ).order_by("-created_at").first()
      )

    return statement

  def _extract_financial_data(self, financial_statement: FinancialStatement) -> Dict:
    """재무제표에서 주요 수치 추출"""
    # 모든 항목 조회
    items = FinancialStatementItem.objects.filter(statement=financial_statement).select_related("account")

    # account_id로 매핑
    items_dict = {item.account.account_id: item for item in items}

    # 당기순이익 (IS) - 지배기업 소유주지분 우선
    net_income = self._get_account_amount(
      items_dict,
      [
        "ifrs-full_ProfitLossAttributableToOwnersOfParent",  # 지배기업 소유주지분 (가장 정확)
        "ifrs-full_Profit",  # 당기순이익
        "ifrs_NetIncome",
        "ifrs-full_NetIncome",
        "ifrs-full_ProfitLoss",  # 이 값은 종종 0이므로 마지막 순위
      ]
    )

    # 자본총계 (BS)
    total_equity = self._get_account_amount(items_dict, ["ifrs-full_Equity", "ifrs_Equity", "ifrs-full_TotalEquity"])

    # 자산총계 (BS)
    total_assets = self._get_account_amount(items_dict, ["ifrs-full_Assets", "ifrs_Assets", "ifrs-full_TotalAssets"])

    # 부채총계 (BS) - 자본 계산 fallback용
    total_liabilities = self._get_account_amount(
      items_dict, ["ifrs-full_Liabilities", "ifrs_Liabilities", "ifrs-full_TotalLiabilities"]
    )

    # 배당금 지급 (CF) - 현금흐름표
    dividends_paid = self._get_account_amount(
      items_dict,
      [
        "ifrs-full_DividendsPaidClassifiedAsFinancingActivities",  # 재무활동으로 분류된 배당금 지급 (가장 일반적)
        "ifrs-full_DividendsPaid",  # 배당금 지급
      ]
    )

    # 자본총계 검증 및 보정
    # 자본이 자산의 1% 미만이면 데이터 오류로 판단하여 재계산
    if total_equity and total_assets:
      equity_ratio = (total_equity / total_assets) * 100
      if equity_ratio < 1:  # 자본비율이 1% 미만이면 이상
        logger.warning(
          f"자본총계가 비정상적으로 작음 ({equity_ratio:.2f}%). "
          f"Assets - Liabilities로 재계산. "
          f"원본 Equity: {total_equity:,}, Assets: {total_assets:,}"
        )
        if total_liabilities is not None:
          calculated_equity = total_assets - total_liabilities
          logger.info(f"재계산된 자본총계: {calculated_equity:,}")
          total_equity = calculated_equity

    return {
      "net_income": net_income,
      "total_equity": total_equity,
      "total_assets": total_assets,
      # dividends_paid는 DPS 계산에만 사용되고 별도 필드로 저장하지 않음
      "_dividends_paid": dividends_paid,  # 언더스코어로 내부 사용 표시
      "calculation_notes": {
        "net_income_account":
        self._find_used_account(
          items_dict, [
            "ifrs-full_ProfitLossAttributableToOwnersOfParent",
            "ifrs-full_Profit",
            "ifrs_NetIncome",
            "ifrs-full_NetIncome",
            "ifrs-full_ProfitLoss",
          ]
        ),
        "equity_account":
        self._find_used_account(items_dict, ["ifrs-full_Equity", "ifrs_Equity", "ifrs-full_TotalEquity"]),
        "assets_account":
        self._find_used_account(items_dict, ["ifrs-full_Assets", "ifrs_Assets", "ifrs-full_TotalAssets"]),
        "dividends_paid_account":
        self._find_used_account(
          items_dict, [
            "ifrs-full_DividendsPaidClassifiedAsFinancingActivities",
            "ifrs-full_DividendsPaid",
          ]
        ),
        "dividends_paid":
        str(dividends_paid) if dividends_paid is not None else None,
        "fiscal_quarter":
        financial_statement.fiscal_quarter,
        "report_type":
        financial_statement.report_type,
      },
    }

  def _get_account_amount(self, items_dict: Dict, account_ids: list) -> Optional[Decimal]:
    """여러 account_id 중 유효한 값이 있으면 금액 반환

    0이 아닌 값을 우선적으로 찾고, 모든 계정이 0이거나 None이면 0 반환
    """
    zero_value = None  # 0 값을 발견하면 저장

    for account_id in account_ids:
      if account_id in items_dict:
        item = items_dict[account_id]
        # current_amount 확인
        if item.current_amount is not None:
          if item.current_amount != 0:
            return item.current_amount  # 0이 아닌 값 발견 시 즉시 반환
          else:
            zero_value = Decimal("0")  # 0 값 저장
        # cumulative_amount 확인
        elif item.cumulative_amount is not None:
          if item.cumulative_amount != 0:
            return item.cumulative_amount
          else:
            zero_value = Decimal("0")

    # 모든 계정이 0이거나 None인 경우
    return zero_value

  def _find_used_account(self, items_dict: Dict, account_ids: list) -> Optional[str]:
    """실제 사용된 account_id 반환"""
    for account_id in account_ids:
      if account_id in items_dict:
        return account_id
    return None

  def _get_reference_stock_price(
    self,
    fiscal_year: int,
    fiscal_quarter: int,
    reference_date: Optional[date] = None,
  ) -> Optional[StockPrice]:
    """기준일 주가 조회

    reference_date가 주어지면 해당 날짜의 주가를 찾고,
    없으면 분기 말일에 가장 가까운 주가를 찾습니다.
    """
    if reference_date:
      # 지정된 날짜의 주가
      return (StockPrice.objects.filter(stock=self.stock, trade_date=reference_date).order_by("-trade_date").first())

    # 분기 말일 계산
    quarter_end_month = fiscal_quarter * 3
    if quarter_end_month == 12:
      quarter_end_date = date(fiscal_year, 12, 31)
    else:
      # 다음 달 1일 - 1일
      from calendar import monthrange

      last_day = monthrange(fiscal_year, quarter_end_month)[1]
      quarter_end_date = date(fiscal_year, quarter_end_month, last_day)

    # 분기 말일 이전 가장 가까운 거래일의 주가
    return (
      StockPrice.objects.filter(stock=self.stock, trade_date__lte=quarter_end_date).order_by("-trade_date").first()
    )

  def _calculate_indicators(
    self,
    financial_data: Dict,
    reference_price: Optional[Decimal],
    total_shares: Optional[int],
    fiscal_quarter: int,
  ) -> Dict:
    """파생지표 계산

    Args:
      financial_data: 재무제표 데이터
      reference_price: 기준 주가
      total_shares: 총 주식수
      fiscal_quarter: 분기 (1-4)
    """
    indicators = {}

    net_income = financial_data.get("net_income")
    total_equity = financial_data.get("total_equity")
    total_assets = financial_data.get("total_assets")
    dividends_paid = financial_data.get("_dividends_paid")  # 언더스코어 키 사용

    # 분기 데이터 연환산 계수
    # Q1 (3개월): x4, Q2 (6개월): x2, Q3 (9개월): x(4/3), Q4 (12개월): x1
    annualization_factors = {
      1: Decimal("4.0"),  # Q1: 3개월 → 12개월
      2: Decimal("2.0"),  # Q2: 6개월 → 12개월
      3: Decimal("1.3333"),  # Q3: 9개월 → 12개월 (4/3)
      4: Decimal("1.0"),  # Q4: 12개월 (연환산 불필요)
    }
    annualization_factor = annualization_factors.get(fiscal_quarter, Decimal("1.0"))

    # 연환산 당기순이익 (ROE, ROA, PER 계산용)
    annualized_net_income = None
    if net_income is not None:
      annualized_net_income = net_income * annualization_factor

    # EPS 계산 (주당순이익 - 연환산)
    if annualized_net_income is not None and total_shares and total_shares > 0:
      eps = annualized_net_income / Decimal(total_shares)
      indicators["eps"] = eps
    else:
      eps = None
      indicators["eps"] = None

    # BPS 계산 (주당순자산 - 시점 데이터이므로 연환산 불필요)
    if total_equity is not None and total_shares and total_shares > 0:
      bps = total_equity / Decimal(total_shares)
      indicators["bps"] = bps
    else:
      bps = None
      indicators["bps"] = None

    # PER 계산 (주가수익비율 - 연환산 EPS 사용)
    if reference_price and eps and eps > 0:
      indicators["per"] = reference_price / eps
    else:
      indicators["per"] = None

    # PBR 계산 (주가순자산비율)
    if reference_price and bps and bps > 0:
      indicators["pbr"] = reference_price / bps
    else:
      indicators["pbr"] = None

    # ROE 계산 (자기자본이익률 - 연환산)
    if annualized_net_income is not None and total_equity and total_equity > 0:
      indicators["roe"] = (annualized_net_income / total_equity) * 100
    else:
      indicators["roe"] = None

    # ROA 계산 (총자산이익률 - 연환산)
    if annualized_net_income is not None and total_assets and total_assets > 0:
      indicators["roa"] = (annualized_net_income / total_assets) * 100
    else:
      indicators["roa"] = None

    # DPS 계산 (주당배당금)
    if dividends_paid is not None and total_shares and total_shares > 0:
      # 배당금 지급액을 주식수로 나눔
      dps = dividends_paid / Decimal(total_shares)
      indicators["dps"] = dps
    else:
      dps = None
      indicators["dps"] = None

    # 배당수익률 계산
    if reference_price and dps and dps > 0:
      # (DPS / 주가) × 100
      indicators["dividend_yield"] = (dps / reference_price) * 100
    else:
      indicators["dividend_yield"] = None

    return indicators

  def calculate_all_available_periods(self) -> list[DerivedIndicator]:
    """사용 가능한 모든 기간의 파생지표 계산"""
    logger.info(f"모든 기간 파생지표 계산 시작: {self.stock.name}")

    # 회사의 모든 재무제표 조회
    financial_statements = FinancialStatement.objects.filter(company=self.company
                                                             ).values_list("fiscal_year", "fiscal_quarter", named=True)

    results = []
    for fs in financial_statements:
      indicator = self.calculate_for_period(fs.fiscal_year, fs.fiscal_quarter)
      if indicator:
        results.append(indicator)

    logger.info(f"모든 기간 파생지표 계산 완료: {self.stock.name} - {len(results)}개")
    return results


def calculate_derived_indicators_for_company(company: Company, ) -> Dict[str, list[DerivedIndicator]]:
  """회사의 모든 주식에 대해 파생지표 계산

  Args:
    company: 대상 회사

  Returns:
    {stock_code: [DerivedIndicator, ...]} 형태의 딕셔너리
  """
  logger.info(f"회사 파생지표 계산 시작: {company.name}")

  results = {}
  stocks = company.stocks.filter(is_listed=True)

  for stock in stocks:
    service = DerivedIndicatorService(stock)
    indicators = service.calculate_all_available_periods()
    results[stock.code] = indicators

  logger.info(f"회사 파생지표 계산 완료: {company.name} - {len(results)}개 종목")
  return results
