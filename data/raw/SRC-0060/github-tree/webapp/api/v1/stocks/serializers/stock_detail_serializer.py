from rest_framework import serializers
from stocks.models import Stock

from api.v1.companies.serializers import (
  CompanySerializer,
)

from .market_serializer import (
  MarketSerializer,
)


class StockDetailSerializer(serializers.ModelSerializer):
  """Stock detail serializer - includes company and market information"""

  company = CompanySerializer(read_only=True)
  market = MarketSerializer(read_only=True)
  prices_count = serializers.SerializerMethodField()
  latest_price = serializers.SerializerMethodField()

  class Meta:
    model = Stock
    fields = [
      "code",
      "name",
      "company",
      "market",
      "category",
      "is_primary",
      "is_listed",
      "listed_date",
      "delisted_date",
      "currency",
      "lot_size",
      "prices_count",
      "latest_price",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields

  def get_prices_count(self, obj: Stock) -> int:
    """Get the count of stock prices"""
    return obj.prices.count()

  def get_latest_price(self, obj: Stock) -> dict | None:
    """Get the latest stock price"""
    latest = obj.prices.order_by("-trade_date").first()
    if latest:
      return {
        "trade_date": latest.trade_date,
        "close_price": latest.close_price,
        "diff": latest.diff,
        "change_rate": latest.change_rate,
        "open_price": latest.open_price,
        "high_price": latest.high_price,
        "low_price": latest.low_price,
        "volume": latest.volume,
        "value": latest.value,
        "market_cap": latest.market_cap,
        "shares": latest.shares,
      }
    return None
