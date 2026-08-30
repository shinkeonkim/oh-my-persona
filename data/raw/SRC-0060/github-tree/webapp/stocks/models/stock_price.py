from django.db import models

from common.models import BaseModel


class StockPrice(BaseModel):
  """
    주식 가격 모델

    일자별 주식 가격 데이터를 저장하는 모델
    """

  class Meta:
    db_table = "stock_prices"
    verbose_name = "Stock Price"
    verbose_name_plural = "Stock Prices"
    ordering = ["-trade_date", "stock"]
    indexes = [
      models.Index(fields=["stock", "trade_date"], name="idx_stock_date"),
      models.Index(fields=["market", "trade_date"], name="idx_market_date"),
      models.Index(fields=["trade_date"], name="idx_trade_date"),
    ]
    constraints = [
      models.UniqueConstraint(
        fields=["trade_date", "market", "stock"],
        name="unique_trade_date_market_stock",
      ),
    ]

  # 거래 기본 정보
  trade_date = models.DateField(verbose_name="거래일")

  market = models.ForeignKey(
    "stocks.Market",
    on_delete=models.PROTECT,
    related_name="stock_prices",
    verbose_name="시장",
  )

  stock = models.ForeignKey(
    "stocks.Stock",
    on_delete=models.CASCADE,
    related_name="prices",
    verbose_name="종목",
  )

  # 가격 정보
  close_price = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    verbose_name="종가",
  )
  diff = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    verbose_name="전일 대비",
  )
  change_rate = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    verbose_name="등락률 (%)",
  )
  open_price = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    verbose_name="시가",
  )
  high_price = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    verbose_name="고가",
  )
  low_price = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    verbose_name="저가",
  )

  # 거래량 정보
  volume = models.BigIntegerField(verbose_name="거래량")
  value = models.BigIntegerField(verbose_name="거래대금")

  # 시가총액 정보
  market_cap = models.BigIntegerField(verbose_name="시가총액")
  shares = models.BigIntegerField(verbose_name="상장주식수")

  def __str__(self) -> str:
    return f"{self.stock.code} - {self.trade_date}: {self.close_price}"
