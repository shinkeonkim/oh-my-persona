from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.permissions import ReferralPermission
from api.v1.matchmakings.serializers import ReferralSerializer
from api.v1.matchmakings.services import ReferralService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import get_unauthorized_error_schema
from common.utils.logger import get_logger

logger = get_logger(__name__)


@extend_schema(tags=["추천"])
class LatestReferralAPIView(BaseMatchmakingAPIView):
  """가장 최근 추천 조회 전용 뷰"""

  permission_classes = [IsAuthenticated, ReferralPermission]

  @extend_schema(
    operation_id="get_latest_referral",
    summary="가장 최근 추천 조회",
    description="사용자가 받은 가장 최근 추천을 조회합니다. 알고리즘 타입으로 필터링 가능합니다.",
    responses={
      200: OpenApiResponse(
        response=ReferralSerializer,
        description="가장 최근 추천 조회 성공",
      ),
      401: get_unauthorized_error_schema(),
    },
  )
  def get(self, request):
    """가장 최근 추천 조회"""
    algorithm_type = request.query_params.get("algorithm_type")

    latest_referral = ReferralService.get_latest_referral(self.current_user, algorithm_type)

    serializer = ReferralSerializer(latest_referral, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
