from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.exceptions import ReferralNotFoundError
from common.exceptions.custom_exceptions import NotFoundError
from common.schemas.error_schemas import (
  get_internal_server_error_schema,
  get_not_found_error_schema,
  get_unauthorized_error_schema,
)
from common.utils.logger import get_logger

from ..serializers import CompatibilityScoreSerializer
from .base_referral_profile_api_view import BaseReferralProfileAPIView

logger = get_logger(__name__)


@extend_schema(tags=["프로필"])
class CompatibilityScoreAPIView(BaseReferralProfileAPIView):
  """추천 궁합 점수 API 뷰"""

  permission_classes = [IsAuthenticated]

  @extend_schema(
    operation_id="get_profile_compatibility_score",
    summary="최근 추천의 궁합 점수 조회",
    description="사용자의 가장 최근 추천에 대한 궁합 점수를 조회합니다.",
    responses={
      200: OpenApiResponse(
        response=CompatibilityScoreSerializer,
        description="궁합 점수 조회 성공",
      ),
      401: get_unauthorized_error_schema(),
      404: get_not_found_error_schema(),
      500: get_internal_server_error_schema(),
    },
  )
  def get(self, request, profile_id):
    """최근 추천의 궁합 점수 조회"""
    try:
      # 가장 최근 추천 조회
      latest_referral = self.get_latest_referral(profile_id)

      # 궁합 점수 반환
      serializer = CompatibilityScoreSerializer({"compatibility_score": latest_referral.compatibility_score})
      return Response(serializer.data, status=status.HTTP_200_OK)

    except ReferralNotFoundError:
      raise NotFoundError(message="해당 프로필에 대한 추천을 찾을 수 없습니다.", )
