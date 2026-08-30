from rest_framework import serializers

from saju.models import SajuProfile


class SajuProfileListSerializer(serializers.ModelSerializer):

  class Meta:
    model = SajuProfile
    fields = [
      "d_stem",
      "d_branch",
    ]
    read_only_fields = fields
