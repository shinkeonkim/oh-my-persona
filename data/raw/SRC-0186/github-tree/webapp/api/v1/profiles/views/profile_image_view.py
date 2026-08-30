from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from profiles.models import Profile

from ..exceptions.profile_exceptions import ProfileNotFoundError
from ..permissions import ConfirmedUserPermission, ProfileAccessPermission
from ..schemas.error_schemas import get_file_not_found_error_schema
from ..serializers import ProfileImageSerializer


@extend_schema(tags=["Profile Image"])
class ProfileImageViewSet(
    GenericViewSet,
    ListModelMixin,
):
  """다른 사용자의 프로필 이미지 조회 ViewSet (읽기 전용)"""

  serializer_class = ProfileImageSerializer
  permission_classes = [
    IsAuthenticated,
    ConfirmedUserPermission,
    ProfileAccessPermission,
  ]

  def get_queryset(self):
    """Get profile images for the specified profile"""
    profile_id = self.kwargs.get("profile_id")
    try:
      profile = Profile.objects.get(id=profile_id)
      # Profile에 대한 접근 권한 확인
      self.check_object_permissions(self.request, profile)
      return profile.profile_images.all()
    except Profile.DoesNotExist:
      raise ProfileNotFoundError()

  @extend_schema(
    operation_id="list_profile_images",
    summary="List Profile Images",
    description="Retrieve all profile images for a specific user profile.",
    parameters=[
      OpenApiParameter(
        name="profile_id",
        type=int,
        location=OpenApiParameter.PATH,
        description="Profile ID",
      )
    ],
    responses={
      200: OpenApiResponse(
        response=ProfileImageSerializer,
        description="Profile images retrieved successfully",
      ),
      404: get_file_not_found_error_schema(),
    },
  )
  def list(self, request, *args, **kwargs):
    """Get profile images for a specific profile"""
    return super().list(request, *args, **kwargs)
