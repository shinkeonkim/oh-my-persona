from django.db import models

from stocks.choices import StockCategoryChoice

from common.choices import CurrencyChoice
from common.models import BaseModel, BaseModelManager, BaseModelQuerySet


class StockQuerySet(BaseModelQuerySet):

  def listed(self):
    return self.filter(is_listed=True)

  def delisted(self):
    return self.filter(is_listed=False)

  def primary(self):
    return self.filter(is_primary=True)


class StockManager(BaseModelManager.from_queryset(StockQuerySet)):
  pass


class Stock(BaseModel):
  """개별 주식 종목 모델

    한 회사가 여러 주식(보통주, 우선주 등)을 상장할 수 있으므로
    Company와 Stock을 분리하여 관리합니다.

    예시:
    - 삼성전자(Company) -> 삼성전자(Stock), 삼성전자우(Stock)
    - LG화학(Company) -> LG화학(Stock)
    """

  class Meta:
    db_table = "stocks"
    verbose_name = "Stock"
    verbose_name_plural = "Stocks"
    indexes = [
      models.Index(fields=["name"], name="idx_stock_name"),
      models.Index(fields=["market", "company"], name="idx_stock_company_market"),
      models.Index(fields=["is_primary", "company"], name="idx_stock_is_primary"),
      models.Index(fields=["is_listed"], name="idx_stock_is_listed"),
      # 파생지표 필터링을 위한 인덱스
      models.Index(fields=["latest_per"], name="idx_stock_latest_per"),
      models.Index(fields=["latest_pbr"], name="idx_stock_latest_pbr"),
      models.Index(fields=["latest_roe"], name="idx_stock_latest_roe"),
      models.Index(fields=["latest_roa"], name="idx_stock_latest_roa"),
      models.Index(fields=["latest_dividend_yield"], name="idx_stock_latest_div_yield"),
    ]

  objects = StockManager()

  company = models.ForeignKey(
    "companies.Company",
    on_delete=models.CASCADE,
    related_name="stocks",
    verbose_name="회사",
  )
  market = models.ForeignKey(
    "stocks.Market",
    on_delete=models.PROTECT,
    related_name="stocks",
    verbose_name="시장",
  )

  code = models.CharField(max_length=100, unique=True, verbose_name="종목 코드 (Ticker)")  # ex) 삼성전자: 005930

  name = models.CharField(
    max_length=255,
    verbose_name="종목명",
  )

  # 주식 종류 (보통주, 우선주 등)
  category = models.CharField(
    max_length=20,
    choices=StockCategoryChoice.choices,
    default=StockCategoryChoice.COMMON,
    verbose_name="주식 종류",
  )

  # 회사의 대표 주식 여부
  is_primary = models.BooleanField(
    default=False,
    verbose_name="대표 주식 여부",
  )

  # 상장 정보
  is_listed = models.BooleanField(
    default=True,
    verbose_name="상장 여부",
  )
  listed_date = models.DateField(
    null=True,
    blank=True,
    verbose_name="상장일",
  )
  delisted_date = models.DateField(
    null=True,
    blank=True,
    verbose_name="상장폐지일",
  )

  # 거래 정보
  currency = models.CharField(
    max_length=10,
    choices=CurrencyChoice.choices,
    default=CurrencyChoice.KRW,
    verbose_name="통화",
  )
  lot_size = models.IntegerField(
    default=1,
    verbose_name="거래 단위",
  )

  # 최신 파생지표 캐싱 (성능 최적화)
  latest_per = models.DecimalField(
    max_digits=12,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="최신 PER",
    help_text="가장 최근 분기의 PER",
  )
  latest_eps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="최신 EPS",
    help_text="가장 최근 분기의 EPS",
  )
  latest_pbr = models.DecimalField(
    max_digits=12,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="최신 PBR",
    help_text="가장 최근 분기의 PBR",
  )
  latest_bps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="최신 BPS",
    help_text="가장 최근 분기의 BPS",
  )
  latest_roe = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="최신 ROE (%)",
    help_text="가장 최근 분기의 ROE",
  )
  latest_roa = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="최신 ROA (%)",
    help_text="가장 최근 분기의 ROA",
  )
  latest_dividend_yield = models.DecimalField(
    max_digits=10,
    decimal_places=4,
    null=True,
    blank=True,
    verbose_name="최신 배당수익률 (%)",
    help_text="가장 최근 분기의 배당수익률",
  )
  latest_dps = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True,
    verbose_name="최신 DPS",
    help_text="가장 최근 분기의 DPS",
  )
  latest_indicator_updated_at = models.DateTimeField(
    null=True,
    blank=True,
    verbose_name="최신 지표 업데이트 시각",
    help_text="최신 파생지표가 캐시된 시각",
  )

  def __str__(self) -> str:
    return f"{self.name} ({self.code})"

  def update_latest_indicators(self) -> None:
    """최신 파생지표를 캐시에 업데이트"""
    from django.utils import timezone

    from stocks.models import DerivedIndicator

    # 업데이트할 필드 목록 (Stock 필드명, DerivedIndicator 필드명)
    indicator_fields = [
      ("latest_per", "per"),
      ("latest_eps", "eps"),
      ("latest_pbr", "pbr"),
      ("latest_bps", "bps"),
      ("latest_roe", "roe"),
      ("latest_roa", "roa"),
      ("latest_dividend_yield", "dividend_yield"),
      ("latest_dps", "dps"),
    ]

    latest_indicator = (DerivedIndicator.objects.filter(stock=self).order_by("-fiscal_year", "-fiscal_quarter").first())

    if latest_indicator:
      for stock_field, indicator_field in indicator_fields:
        setattr(self, stock_field, getattr(latest_indicator, indicator_field))
      self.latest_indicator_updated_at = timezone.now()
    else:
      for stock_field, _ in indicator_fields:
        setattr(self, stock_field, None)
      self.latest_indicator_updated_at = None

    update_fields = [field[0] for field in indicator_fields] + ["latest_indicator_updated_at"]
    self.save(update_fields=update_fields)
