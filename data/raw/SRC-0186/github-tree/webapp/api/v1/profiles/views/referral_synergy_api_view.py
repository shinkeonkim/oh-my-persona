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
from matchmakings.choices import GenerationStatusChoice

from ..serializers import ReferralSynergySerializer
from .base_referral_profile_api_view import BaseReferralProfileAPIView

logger = get_logger(__name__)


@extend_schema(tags=["프로필"])
class ReferralSynergyAPIView(BaseReferralProfileAPIView):
  """추천 천생연분 시너지 API 뷰"""

  permission_classes = [IsAuthenticated]

  @extend_schema(
    operation_id="get_profile_referral_synergies",
    summary="최근 추천의 천생연분 시너지 조회",
    description="사용자의 가장 최근 추천에 대한 천생연분 시너지 정보(3개)를 조회합니다.",
    responses={
      200: OpenApiResponse(
        response=ReferralSynergySerializer(many=True),
        description="시너지 조회 성공",
      ),
      401: get_unauthorized_error_schema(),
      404: get_not_found_error_schema(),
      500: get_internal_server_error_schema(),
    },
  )
  def get(self, request, profile_id):
    """최근 추천의 천생연분 시너지 조회"""
    try:
      latest_referral = self.get_latest_referral(profile_id=profile_id)

      is_not_completed = latest_referral.synergy_generation_status != GenerationStatusChoice.COMPLETED
      has_no_synergies = not hasattr(latest_referral, 'synergies')

      if is_not_completed or has_no_synergies:
        raise NotFoundError(message="아직 천생연분 시너지가 생성되고 있습니다.", details={"referral_id": latest_referral.id})

      # 해당 추천의 시너지들 조회
      synergies = latest_referral.synergies.all()

      serializer = ReferralSynergySerializer(synergies, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

    except ReferralNotFoundError:
      raise NotFoundError(message="해당 프로필에 대한 추천을 찾을 수 없습니다.", details={"profile_id": profile_id})
