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

from ..serializers import ReferralOverallOpinionSerializer
from .base_referral_profile_api_view import BaseReferralProfileAPIView

logger = get_logger(__name__)


@extend_schema(tags=["프로필"])
class ReferralOverallOpinionAPIView(BaseReferralProfileAPIView):
  """추천 종합의견 API 뷰"""

  permission_classes = [IsAuthenticated]

  @extend_schema(
    operation_id="get_profile_referral_overall_opinion",
    summary="최근 추천의 종합의견 조회",
    description="사용자의 가장 최근 추천에 대한 중개인의 종합의견을 조회합니다. 사용자의 성별에 따라 적절한 의견을 반환합니다.",
    responses={
      200: OpenApiResponse(
        response=ReferralOverallOpinionSerializer,
        description="종합의견 조회 성공",
      ),
      401: get_unauthorized_error_schema(),
      404: get_not_found_error_schema(),
      500: get_internal_server_error_schema(),
    },
  )
  def get(self, request, profile_id):
    """최근 추천의 종합의견 조회"""
    try:
      latest_referral = self.get_latest_referral(profile_id=profile_id)

      # 종합의견이 아직 생성되지 않은 경우
      if not hasattr(latest_referral, 'overall_opinion'):
        raise NotFoundError(message="아직 생성되지 않은 종합의견입니다.", details={"referral_id": latest_referral.id})

      overall_opinion = latest_referral.overall_opinion

      if not overall_opinion.generation_status == GenerationStatusChoice.COMPLETED:
        raise NotFoundError(message="아직 종합 의견이 생성되고 있습니다.", details={"referral_id": latest_referral.id})

      serializer = ReferralOverallOpinionSerializer(latest_referral.overall_opinion, context={"request": request})
      return Response(serializer.data, status=status.HTTP_200_OK)

    except ReferralNotFoundError:
      raise NotFoundError(message="해당 프로필에 대한 추천을 찾을 수 없습니다.", details={"profile_id": profile_id})
