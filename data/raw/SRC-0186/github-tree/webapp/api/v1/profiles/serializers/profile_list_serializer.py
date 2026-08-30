from rest_framework import serializers

from profiles.models import Profile

from .profile_image_serializer import ProfileImageSerializer
from .saju_profile_list_serializer import SajuProfileListSerializer


class ProfileListSerializer(serializers.ModelSerializer):
  """프로필 목록용 시리얼라이저 (간소화)"""
  username = serializers.CharField(source="user.username", read_only=True)
  saju_profile = SajuProfileListSerializer(read_only=True)
  representative_image = ProfileImageSerializer(read_only=True)

  class Meta:
    model = Profile
    fields = [
      "id",
      "age",
      "one_liner",
      "region",
      "saju_profile",
      "representative_image",
      "username",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "age",
      "one_liner",
      "region",
      "saju_profile",
      "representative_image",
      "username",
      "created_at",
      "updated_at",
    ]
