from rest_framework import serializers

from api.v1.profiles.serializers.job_info_serializer import JobInfoSerializer
from profiles.models import Profile

from .profile_image_serializer import ProfileImageSerializer
from .saju_profile_serializer import SajuProfileSerializer


class ProfileSerializer(serializers.ModelSerializer):
  """다른 사용자의 프로필 조회용 시리얼라이저 (읽기 전용)"""

  username = serializers.CharField(source="user.username", read_only=True)
  job_info = JobInfoSerializer(read_only=True)
  saju_profile = SajuProfileSerializer(read_only=True)
  representative_image = ProfileImageSerializer(read_only=True)

  class Meta:
    model = Profile
    fields = [
      "id",
      "username",
      "mbti",
      "region",
      "city",
      "job_info",
      "gender",
      "birth_time",
      "age",
      "introduction",
      "one_liner",
      "tmi",
      "representative_image",
      "saju_profile",
      "created_at",
      "updated_at",
    ]
    read_only_fields = [
      "id",
      "username",
      "mbti",
      "region",
      "city",
      "job_info",
      "gender",
      "birth_time",
      "age",
      "introduction",
      "one_liner",
      "tmi",
      "representative_image",
      "saju_profile",
      "created_at",
      "updated_at",
    ]
