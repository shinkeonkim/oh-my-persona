from django.db import transaction

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response

from common.utils.logger import get_logger
from profiles.models import Profile

from ..permissions import ProfilePermission
from ..schemas.error_schemas import get_profile_validation_error_schema
from ..serializers import MyProfileSerializer
from .base_profile_api_view import BaseProfileAPIView

logger = get_logger(__name__)


@extend_schema(tags=["내 프로필"])
class MyProfileView(BaseProfileAPIView):
  serializer_class = MyProfileSerializer
  permission_classes = [ProfilePermission]

  def get_object(self):
    """사용자의 프로필을 조회하거나 생성"""
    profile, created = Profile.objects.select_related("job_info", "job_info__job",
                                                      "job_info__job_category").get_or_create(user=self.current_user,
                                                                                              defaults={})
    return profile

  @extend_schema(
    operation_id="get_user_profile",
    summary="사용자 프로필 조회",
    description="인증된 사용자의 프로필을 조회합니다. 프로필이 없으면 빈 프로필을 생성합니다.",
    responses={200: OpenApiResponse(
      response=MyProfileSerializer,
      description="프로필 조회 성공",
    )},
  )
  def get(self, request):
    """사용자의 프로필 조회 (없으면 생성)"""
    profile = self.get_object()
    serializer = self.get_serializer(profile)
    return Response(serializer.data)

  @extend_schema(
    operation_id="update_user_profile",
    summary="사용자 프로필 업데이트",
    description="인증된 사용자의 프로필을 업데이트합니다. 프로필이 없으면 새로 생성합니다. job_info를 통해 직업 정보를 관리합니다.",
    request=MyProfileSerializer,
    responses={
      200: OpenApiResponse(response=MyProfileSerializer, description="프로필 업데이트 성공"),
      422: get_profile_validation_error_schema(),
    },
  )
  @transaction.atomic
  def patch(self, request):
    """사용자의 프로필 업데이트 (없으면 생성)"""
    profile = self.get_object()
    should_unconfirm = self._check_onboarding_fields_changed(profile, request.data)

    serializer = self.get_serializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)

    # 온보딩 필드가 변경된 경우에만 사용자 승인 취소
    if should_unconfirm and self.current_user.is_confirmed:
      self.current_user.unconfirm()
      logger.info(f"사용자 {self.current_user.email} (ID: {self.current_user.id})의 온보딩 필드 변경으로 승인 취소")

    serializer.save()
    return Response(serializer.data)

  def _check_onboarding_fields_changed(self, profile, data):
    """온보딩 필드(birth_time, mbti, region, city, job_info) 변경 여부 확인"""

    onboarding_fields = ["birth_time", "mbti", "region", "city"]

    # 일반 필드 확인
    for field in onboarding_fields:
      if field in data:
        original_value = getattr(profile, field, None)
        new_value = data[field]
        if original_value != new_value:
          logger.debug(f"필드 '{field}' 변경 감지: {original_value} -> {new_value}")
          return True

    # job_info 필드 확인 (nested object)
    if "job_info" in data:
      job_info_data = data["job_info"]
      original_job_info = profile.job_info

      # job_info가 None에서 생성되는 경우
      if original_job_info is None and job_info_data:
        logger.debug("job_info 생성 감지")
        return True

      # job_info가 있는 경우 세부 필드 확인
      if original_job_info and job_info_data:
        # job_id 변경 확인
        if "job_id" in job_info_data:
          original_job_id = original_job_info.job_id if original_job_info.job else None
          new_job_id = job_info_data["job_id"]
          if original_job_id != new_job_id:
            logger.debug(f"job_id 변경 감지: {original_job_id} -> {new_job_id}")
            return True

        # job_category_id 변경 확인
        if "job_category_id" in job_info_data:
          original_category_id = original_job_info.job_category_id if original_job_info.job_category else None
          new_category_id = job_info_data["job_category_id"]
          if original_category_id != new_category_id:
            logger.debug(f"job_category_id 변경 감지: {original_category_id} -> {new_category_id}")
            return True

        # manual_job 변경 확인
        if "manual_job" in job_info_data:
          original_manual_job = original_job_info.manual_job or ""
          new_manual_job = job_info_data["manual_job"] or ""
          if original_manual_job != new_manual_job:
            logger.debug(f"manual_job 변경 감지: {original_manual_job} -> {new_manual_job}")
            return True

        # manual_job_category 변경 확인
        if "manual_job_category" in job_info_data:
          original_manual_category = original_job_info.manual_job_category or ""
          new_manual_category = job_info_data["manual_job_category"] or ""
          if original_manual_category != new_manual_category:
            logger.debug(f"manual_job_category 변경 감지: {original_manual_category} -> {new_manual_category}")
            return True

    return False
