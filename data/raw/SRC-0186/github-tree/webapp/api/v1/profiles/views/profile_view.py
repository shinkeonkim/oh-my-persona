from django.shortcuts import get_object_or_404

from action_trackings.decorators import track_profile_view
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import Profile

from ..permissions import ConfirmedUserPermission, ProfileAccessPermission
from ..schemas.error_schemas import get_profile_not_found_error_schema
from ..serializers.public_profile_serializer import ProfileSerializer
from .base_profile_api_view import BaseProfileAPIView


@extend_schema(tags=["프로필"])
class ProfileView(BaseProfileAPIView):
  """다른 사용자의 프로필 조회 API"""

  serializer_class = ProfileSerializer
  permission_classes = [
    IsAuthenticated,
    ConfirmedUserPermission,
    ProfileAccessPermission,
  ]

  def get_object(self, profile_id):
    """특정 사용자의 프로필을 조회"""
    profile = get_object_or_404(
      Profile.objects.select_related("job_info", "job_info__job", "job_info__job_category"),
      id=profile_id,
    )
    self.check_object_permissions(self.request, profile)
    return profile

  @extend_schema(
    operation_id="get_user_profile_by_id",
    summary="사용자 프로필 조회",
    description="특정 사용자의 프로필을 조회합니다.",
    responses={
      200: OpenApiResponse(
        response=ProfileSerializer,
        description="프로필 조회 성공",
      ),
      404: get_profile_not_found_error_schema(),
    },
  )
  @track_profile_view(
    get_profile=lambda view, *args, **kwargs: view.get_object(kwargs["profile_id"]),
    get_metadata=lambda view, *args, **kwargs: {
      "source": "profile_detail_api",
      "user_id": view.request.user.id,
    },
  )
  def get(self, request, profile_id):
    """특정 사용자의 프로필 조회"""
    profile = self.get_object(profile_id)
    serializer = self.get_serializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)
