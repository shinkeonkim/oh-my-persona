from rest_framework import serializers
from stocks.models import StockPrice


class StockPriceSerializer(serializers.ModelSerializer):
  """Stock price serializer"""

  class Meta:
    model = StockPrice
    fields = [
      "trade_date",
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
    ]
    read_only_fields = fields
