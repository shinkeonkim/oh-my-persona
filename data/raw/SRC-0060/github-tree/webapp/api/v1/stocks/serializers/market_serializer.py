from rest_framework import serializers
from stocks.models import Market


class MarketSerializer(serializers.ModelSerializer):

  class Meta:
    model = Market
    fields = ["id", "code", "name"]
