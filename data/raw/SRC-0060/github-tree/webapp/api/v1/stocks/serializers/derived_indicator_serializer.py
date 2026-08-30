from rest_framework import serializers
from stocks.models import DerivedIndicator


class DerivedIndicatorSerializer(serializers.ModelSerializer):
  """파생지표 Serializer"""

  stock_code = serializers.CharField(source="stock.code", read_only=True)
  stock_name = serializers.CharField(source="stock.name", read_only=True)
  company_name = serializers.CharField(source="company.name", read_only=True)

  class Meta:
    model = DerivedIndicator
    fields = [
      "id",
      "stock_code",
      "stock_name",
      "company_name",
      "fiscal_year",
      "fiscal_quarter",
      "reference_price",
      "reference_date",
      "market_cap",
      "per",
      "eps",
      "pbr",
      "bps",
      "roe",
      "roa",
      "dividend_yield",
      "dps",
      "net_income",
      "total_equity",
      "total_assets",
      "total_shares",
      "created_at",
      "updated_at",
    ]
    read_only_fields = fields


class DerivedIndicatorDetailSerializer(DerivedIndicatorSerializer):
  """파생지표 상세 Serializer (계산 메모 포함)"""

  class Meta(DerivedIndicatorSerializer.Meta):
    fields = DerivedIndicatorSerializer.Meta.fields + ["calculation_notes"]
