from rest_framework import serializers
from stocks.models import Stock, StockPrice

from .market_serializer import MarketSerializer


class StockSerializer(serializers.ModelSerializer):
  """Stock serializer for company stocks list"""

  market = MarketSerializer(read_only=True)
  company_name = serializers.CharField(source="company.name", read_only=True)

  class Meta:
    model = Stock
    fields = [
      "id",
      "code",
      "name",
      "company_name",
      "market",
      "category",
      "is_primary",
      "is_listed",
      "listed_date",
      "delisted_date",
      "currency",
      "lot_size",
      "latest_per",
      "latest_eps",
      "latest_pbr",
      "latest_bps",
      "latest_roe",
      "latest_roa",
      "latest_dividend_yield",
      "latest_dps",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields


class StockPriceSerializer(serializers.ModelSerializer):
  """Stock price serializer"""

  stock_code = serializers.CharField(source="stock.code", read_only=True)
  stock_name = serializers.CharField(source="stock.name", read_only=True)
  market = MarketSerializer(read_only=True)

  class Meta:
    model = StockPrice
    fields = [
      "id",
      "trade_date",
      "stock_code",
      "stock_name",
      "market",
      "close_price",
      "diff",
      "change_rate",
      "open_price",
      "high_price",
      "low_price",
      "volume",
      "value",
      "market_cap",
      "shares",
      "created_at",
    ]
    read_only_fields = fields
