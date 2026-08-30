from rest_framework import serializers

from api.v1.profiles.serializers.saju_tag_serializer import SajuTagSerializer
from saju.enums import Branch, Stem
from saju.models import SajuProfile
from saju.services.ten_god_service import TenGodService


class SajuProfileSerializer(serializers.ModelSerializer):
  tengod = serializers.SerializerMethodField()
  saju_tags = SajuTagSerializer(many=True, read_only=True)

  def get_tengod(self, obj):
    return TenGodService.compute_pillars_tengods(
      hour_stem=Stem(obj.h_stem),
      day_stem=Stem(obj.d_stem),
      month_stem=Stem(obj.m_stem),
      year_stem=Stem(obj.y_stem),
      hour_branch=Branch(obj.h_branch),
      day_branch=Branch(obj.d_branch),
      month_branch=Branch(obj.m_branch),
      year_branch=Branch(obj.y_branch),
      branch_mode="top",
    )

  class Meta:
    model = SajuProfile
    fields = [
      "y_stem",
      "y_branch",
      "m_stem",
      "m_branch",
      "d_stem",
      "d_branch",
      "h_stem",
      "h_branch",
      "y_stem_element",
      "y_branch_element",
      "m_stem_element",
      "m_branch_element",
      "d_stem_element",
      "d_branch_element",
      "h_stem_element",
      "h_branch_element",
      "tengod",
      "saju_tags",
    ]
    read_only_fields = fields
