from rest_framework import serializers
from stocks.models import Stock
from watchlists.models import Watchlist, WatchlistItem

from api.v1.stocks.serializers import StockSerializer


class WatchlistItemSerializer(serializers.ModelSerializer):
  """Serializer for WatchlistItem scoped to the owner's watchlists"""

  watchlist = serializers.PrimaryKeyRelatedField(queryset=Watchlist.objects.none())
  stock = StockSerializer(read_only=True)
  stock_code = serializers.CharField(write_only=True, required=False)

  class Meta:
    model = WatchlistItem
    fields = (
      "id",
      "watchlist",
      "stock",
      "stock_code",
      "notes",
      "created_at",
      "updated_at",
    )
    read_only_fields = (
      "id",
      "created_at",
      "updated_at",
      "stock",
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    request = self.context.get("request")
    user = getattr(request, "user", None)

    self.fields["watchlist"].queryset = Watchlist.objects.filter(user=user)

  def _assign_stock_from_code(self, validated_data, allow_missing=False):
    stock_code = validated_data.pop("stock_code", None)
    if stock_code is None:
      if allow_missing:
        return validated_data
      raise serializers.ValidationError({"stock_code": "This field is required."})

    try:
      validated_data["stock"] = Stock.objects.get(code=stock_code)
    except Stock.DoesNotExist:
      raise serializers.ValidationError({"stock_code": "Invalid stock code."})

    return validated_data

  def create(self, validated_data):
    validated_data = self._assign_stock_from_code(validated_data)
    return super().create(validated_data)

  def update(self, instance, validated_data):
    validated_data = self._assign_stock_from_code(validated_data, allow_missing=True)
    return super().update(instance, validated_data)
