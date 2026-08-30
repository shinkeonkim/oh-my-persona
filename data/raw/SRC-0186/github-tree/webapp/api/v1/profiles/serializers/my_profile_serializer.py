from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from api.v1.profiles.serializers.job_info_serializer import JobInfoSerializer
from profiles.models import Profile

from .saju_profile_serializer import SajuProfileSerializer


class MyProfileSerializer(WritableNestedModelSerializer):
  """내 프로필 조회 및 수정용 시리얼라이저"""
  username = serializers.CharField(source="user.username", read_only=True)
  job_info = JobInfoSerializer(required=False, allow_null=True)
  saju_profile = SajuProfileSerializer(required=False, allow_null=True)

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
      "age",
      "birth_date",
      "birth_time",
      "introduction",
      "one_liner",
      "tmi",
      "saju_profile",
    ]
    read_only_fields = [
      "id",
      "username",
      "birth_date",
      "saju_profile",
    ]
