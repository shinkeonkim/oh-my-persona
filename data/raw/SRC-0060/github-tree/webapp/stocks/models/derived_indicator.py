from decimal import Decimal

from django.db import models

from common.models import BaseModel


class DerivedIndicator(BaseModel):
  """파생지표 모델

  재무제표와 주가 데이터를 기반으로 계산된 파생지표를 저장합니다.

  주요 지표:
  - PER (Price to Earnings Ratio): 주가수익비율
  - PBR (Price to Book Ratio): 주가순자산비율
  - ROE (Return on Equity): 자기자본이익률
  - ROA (Return on Assets): 총자산이익률
  - 배당수익률 (Dividend Yield)
  """

  class Meta:
    db_table = "derived_indicators"
    verbose_name = "파생지표"
    verbose_name_plural = "파생지표"
    ordering = ["-fiscal_year", "-fiscal_quarter", "stock"]
    indexes = [
      models.Index(fields=["stock", "-fiscal_year", "-fiscal_quarter"], name="idx_di_stock_period"),
      models.Index(fields=["company", "-fiscal_year", "-fiscal_quarter"], name="idx_di_company_period"),
      models.Index(fields=["fiscal_year", "fiscal_quarter"], name="idx_di_period"),
    ]
    constraints = [
      models.UniqueConstraint(
        fields=["stock", "company", "fiscal_year", "fiscal_quarter"],
        name="unique_stock_company_year_quarter",
      )
    ]

  # 관계 필드
  stock = models.ForeignKey(
    "stocks.Stock",
    on_delete=models.CASCADE,
    related_name="derived_indicators",
    verbose_name="종목",
  )
  company = models.ForeignKey(
    "companies.Company",
    on_delete=models.CASCADE,
    related_name="derived_indicators",
    verbose_name="회사",
  )
  financial_statement = models.ForeignKey(
    "financial_statements.FinancialStatement",
    on_delete=models.CASCADE,
    related_name="derived_indicators",
    verbose_name="재무제표",
    null=True,
    blank=True,
  )

  # 기간 정보
  fiscal_year = models.PositiveIntegerField(verbose_name="회계연도")
  fiscal_quarter = models.PositiveSmallIntegerField(verbose_name="분기")

  # 주가 정보 (계산 시점의 주가)
  reference_price = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="기준 주가",
    help_text="지표 계산에 사용된 주가 (분기 말일 종가)",
  )
  reference_date = models.DateField(
    null=True,
    blank=True,
    verbose_name="기준일",
    help_text="기준 주가의 날짜",
  )

  # 시가총액
  market_cap = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="시가총액",
    help_text="기준일 기준 시가총액",
  )

  # PER (Price to Earnings Ratio) - 주가수익비율
  per = models.DecimalField(
    max_digits=12,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="PER",
    help_text="주가수익비율 (Price / EPS)",
  )
  eps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="EPS",
    help_text="주당순이익 (Earnings Per Share)",
  )

  # PBR (Price to Book Ratio) - 주가순자산비율
  pbr = models.DecimalField(
    max_digits=12,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="PBR",
    help_text="주가순자산비율 (Price / BPS)",
  )
  bps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="BPS",
    help_text="주당순자산 (Book value Per Share)",
  )

  # ROE (Return on Equity) - 자기자본이익률
  roe = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="ROE (%)",
    help_text="자기자본이익률 (Net Income / Equity * 100)",
  )

  # ROA (Return on Assets) - 총자산이익률
  roa = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="ROA (%)",
    help_text="총자산이익률 (Net Income / Total Assets * 100)",
  )

  # 배당수익률
  dividend_yield = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="배당수익률 (%)",
    help_text="배당수익률 (DPS / Price * 100)",
  )
  dps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="DPS",
    help_text="주당배당금 (Dividend Per Share)",
  )

  # 재무제표 주요 수치 (참고용 저장)
  net_income = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="당기순이익",
  )
  total_equity = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="자본총계",
  )
  total_assets = models.DecimalField(
    max_digits=24,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="자산총계",
  )
  total_shares = models.BigIntegerField(
    null=True,
    blank=True,
    verbose_name="총 발행주식수",
  )

  # 메타데이터
  calculation_notes = models.JSONField(
    default=dict,
    blank=True,
    verbose_name="계산 메모",
    help_text="계산 과정에서 발생한 특이사항이나 메모",
  )

  def __str__(self) -> str:
    return f"{self.stock.name} {self.fiscal_year}Q{self.fiscal_quarter}"

  @property
  def annualized_net_income(self) -> Decimal | None:
    """연환산 당기순이익 (분기 데이터를 연간으로 환산)"""
    if self.net_income is None:
      return None
    return self.net_income * 4

  @property
  def debt_to_equity_ratio(self) -> Decimal | None:
    """부채비율 계산"""
    if not self.total_assets or not self.total_equity:
      return None
    total_liabilities = self.total_assets - self.total_equity
    if self.total_equity == 0:
      return None
    return (total_liabilities / self.total_equity) * 100
