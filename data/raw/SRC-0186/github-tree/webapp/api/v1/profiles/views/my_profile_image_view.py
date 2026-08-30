from django.db import transaction

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.mixins import (
  CreateModelMixin,
  DestroyModelMixin,
  ListModelMixin,
  RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.schemas.error_schemas import get_validation_error_schema
from profiles.models import MAX_PROFILE_IMAGES, Profile, ProfileImage

from ..exceptions.profile_exceptions import (
  FileNotFoundError,
  ProfileNotFoundError,
  ProfileValidationError,
)
from ..permissions import ProfileImagePermission
from ..schemas.error_schemas import get_file_not_found_error_schema
from ..serializers import ProfileImageSerializer
from .base_profile_api_view import BaseProfileAPIView


@extend_schema(tags=["My Profile Image"])
class MyProfileImageViewSet(
    BaseProfileAPIView,
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
):
  """본인의 프로필 이미지 관리 ViewSet"""

  serializer_class = ProfileImageSerializer
  permission_classes = [ProfileImagePermission]

  def get_queryset(self):
    """Get profile images for the current user"""

    return self.current_user_profile.profile_images.all()

  def get_object(self):
    """Get profile image by ID, ensuring it belongs to the current user"""

    try:
      profile = self.current_user_profile
      return profile.profile_images.get(id=self.kwargs["pk"])
    except Profile.DoesNotExist:
      raise ProfileNotFoundError()
    except ProfileImage.DoesNotExist:
      raise FileNotFoundError("Profile image not found")

  @extend_schema(
    operation_id="list_my_profile_images",
    summary="List My Profile Images",
    description="Retrieve all profile images for the authenticated user.",
    responses={
      200: OpenApiResponse(
        response=ProfileImageSerializer,
        description="Profile images retrieved successfully",
      )
    },
  )
  def list(self, request, *args, **kwargs):
    """Get user's profile images"""
    return super().list(request, *args, **kwargs)

  @extend_schema(
    operation_id="create_my_profile_image",
    summary="Create My Profile Image",
    description=f"""Upload a new profile image for the authenticated user.
    Maximum {MAX_PROFILE_IMAGES} images allowed.""",
    responses={
      201: OpenApiResponse(
        response=ProfileImageSerializer,
        description="Profile image created successfully",
      ),
      422: get_validation_error_schema(),
    },
  )
  @transaction.atomic
  def create(self, request, *args, **kwargs):
    """Create a new profile image"""
    profile = Profile.objects.select_for_update().get(pk=self.current_user_profile.pk)

    if profile.profile_images.count() >= MAX_PROFILE_IMAGES:
      raise ProfileValidationError(
        message=f"프로필당 최대 {MAX_PROFILE_IMAGES}개의 이미지만 업로드할 수 있습니다.",
        details={
          "max_images": MAX_PROFILE_IMAGES,
          "current_count": profile.profile_images.count(),
        },
      )

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save(profile=profile)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

  @extend_schema(
    operation_id="retrieve_my_profile_image",
    summary="Retrieve My Profile Image",
    description="Retrieve a specific profile image by ID for the authenticated user.",
    responses={
      200: OpenApiResponse(
        response=ProfileImageSerializer,
        description="Profile image retrieved successfully",
      ),
      404: get_file_not_found_error_schema(),
    },
  )
  def retrieve(self, request, *args, **kwargs):
    """Get a specific profile image"""
    return super().retrieve(request, *args, **kwargs)

  @extend_schema(
    operation_id="destroy_my_profile_image",
    summary="Delete My Profile Image",
    description="Delete a specific profile image by ID for the authenticated user.",
    responses={
      204: OpenApiResponse(description="Profile image deleted successfully"),
      404: get_file_not_found_error_schema(),
    },
  )
  @transaction.atomic
  def destroy(self, request, *args, **kwargs):
    """Delete a profile image by ID"""
    profile_image = self.get_object()
    profile_image.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
