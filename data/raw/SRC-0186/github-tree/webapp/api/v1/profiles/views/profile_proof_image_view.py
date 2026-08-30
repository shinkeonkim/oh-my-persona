from django.db import transaction

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response

from common.schemas.error_schemas import get_validation_error_schema

from ..exceptions.profile_exceptions import FileNotFoundError
from ..permissions import ProfileProofImagePermission
from ..schemas.error_schemas import get_file_not_found_error_schema
from ..serializers import ProfileProofImageSerializer
from .base_profile_api_view import BaseProfileAPIView


@extend_schema(tags=["프로필 인증 사진"])
class ProfileProofImageView(BaseProfileAPIView):
  """
    프로필 인증 사진 관리 API.
    proof_image는 OneToOneField이므로 단일 리소스로 처리합니다.
    """

  serializer_class = ProfileProofImageSerializer
  permission_classes = [ProfileProofImagePermission]

  def get_object(self):
    return self.current_user_profile

  @extend_schema(
    operation_id="get_user_profile_proof_image",
    summary="프로필 인증 사진 조회",
    description="현재 사용자의 프로필 인증 사진을 조회합니다.",
    responses={
      200: OpenApiResponse(
        response=ProfileProofImageSerializer,
        description="프로필 인증 사진 조회 성공",
      ),
      404: get_file_not_found_error_schema(),
    },
  )
  def get(self, request):
    """사용자의 프로필 인증 사진 조회"""
    profile = self.get_object()
    self.check_object_permissions(request, profile)

    if not profile.proof_image:
      raise FileNotFoundError("Profile proof image not found")

    serializer = self.get_serializer(profile)
    return Response(serializer.data)

  @extend_schema(
    operation_id="upload_user_profile_proof_image",
    summary="프로필 인증 사진 업로드",
    description="인증된 사용자의 프로필 인증 사진을 업로드하거나 업데이트합니다. 기존 인증 사진이 있으면 교체됩니다.",
    responses={
      200: OpenApiResponse(
        response=ProfileProofImageSerializer,
        description="프로필 인증 사진 업로드 성공",
      ),
      201: OpenApiResponse(
        response=ProfileProofImageSerializer,
        description="프로필 인증 사진 생성 성공",
      ),
      422: get_validation_error_schema(),
    },
  )
  @transaction.atomic
  def post(self, request):
    """프로필 인증 사진 업로드 또는 업데이트 (기존 사진이 있으면 교체)"""
    profile = self.get_object()
    self.check_object_permissions(request, profile)

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # 프로필 인증 사진 업로드시 사용자 승인 취소
    if self.current_user.is_confirmed:
      self.current_user.unconfirm()

    serializer.save(profile=profile)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

  @extend_schema(
    operation_id="delete_user_profile_proof_image",
    summary="프로필 인증 사진 삭제",
    description="인증된 사용자의 프로필 인증 사진을 삭제합니다.",
    responses={
      204: OpenApiResponse(description="프로필 인증 사진 삭제 성공"),
      404: get_file_not_found_error_schema(),
    },
  )
  @transaction.atomic
  def delete(self, request):
    """프로필 인증 사진 삭제"""
    profile = self.get_object()
    self.check_object_permissions(request, profile)

    if not profile.proof_image:
      raise FileNotFoundError("Profile proof image not found")

    # 프로필 인증 사진 삭제시 사용자 승인 취소
    if self.current_user.is_confirmed:
      self.current_user.unconfirm()

    # Delete the image file
    profile.proof_image.delete()
    profile.proof_image = None
    profile.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
