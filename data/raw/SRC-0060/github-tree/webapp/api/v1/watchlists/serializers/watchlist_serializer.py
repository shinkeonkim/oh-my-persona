from rest_framework import serializers
from watchlists.models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
  """Serializer for Watchlist belonging to the current user"""

  class Meta:
    model = Watchlist
    fields = (
      "id",
      "name",
      "description",
      "created_at",
      "updated_at",
    )
    read_only_fields = (
      "id",
      "created_at",
      "updated_at",
    )

  def create(self, validated_data):
    """Force ownership to the authenticated user"""
    request = self.context.get("request")
    validated_data["user"] = request.user
    return super().create(validated_data)
