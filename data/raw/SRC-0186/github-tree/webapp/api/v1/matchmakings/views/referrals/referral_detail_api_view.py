from django.db.models import Q

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.permissions import ReferralPermission
from api.v1.matchmakings.schemas.error_schemas import (
  get_no_more_referrals_error_schema,
  get_referral_validation_error_schema,
)
from api.v1.matchmakings.serializers import ReferralSerializer
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.exceptions import NotFoundError
from common.schemas.error_schemas import (
  get_internal_server_error_schema,
  get_unauthorized_error_schema,
)
from common.utils.logger import get_logger
from matchmakings.models import Referral

logger = get_logger(__name__)


@extend_schema(tags=["추천"])
class ReferralDetailAPIView(BaseMatchmakingAPIView):
  """추천 조회 API 뷰"""

  permission_classes = [IsAuthenticated, ReferralPermission]

  @extend_schema(
    operation_id="get_referral_detail",
    summary="추천 상세 조회",
    description="특정 추천의 상세 정보를 조회합니다.",
    request=ReferralSerializer,
    responses={
      200: OpenApiResponse(
        response=ReferralSerializer,
        description="추천 상세 조회 성공",
      ),
      400: get_referral_validation_error_schema(),
      401: get_unauthorized_error_schema(),
      404: get_no_more_referrals_error_schema(),
      500: get_internal_server_error_schema(),
    },
  )
  def get(self, request, referral_id):
    """추천 상세 조회"""
    referral = Referral.objects.filter(Q(user=self.current_user)
                                       | Q(referral_user=self.current_user), ).filter(id=referral_id).first()

    if not referral:
      raise NotFoundError()

    serializer = ReferralSerializer(referral, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
