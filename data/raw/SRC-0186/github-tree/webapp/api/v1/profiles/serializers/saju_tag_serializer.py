from rest_framework import serializers

from saju.models import SajuTag


class SajuTagSerializer(serializers.ModelSerializer):

  class Meta:
    model = SajuTag
    fields = [
      "id",
      "name",
    ]
    read_only_fields = fields
