from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.exceptions import NoMoreReferralsError, ReferralValidationError
from api.v1.matchmakings.permissions import ReferralPermission
from api.v1.matchmakings.schemas.error_schemas import (
  get_no_more_referrals_error_schema,
  get_referral_validation_error_schema,
)
from api.v1.matchmakings.serializers import ReferralCreateSerializer, ReferralSerializer
from api.v1.matchmakings.services import ReferralService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import (
  get_internal_server_error_schema,
  get_unauthorized_error_schema,
)
from common.utils.logger import get_logger
from matchmakings.tasks import generate_referral_llm_messages

logger = get_logger(__name__)


@extend_schema(tags=["추천"])
class CreateReferralAPIView(BaseMatchmakingAPIView):
  """추천 관련 API 뷰"""

  permission_classes = [IsAuthenticated, ReferralPermission]

  @extend_schema(
    operation_id="create_new_referral",
    summary="새로운 추천 생성",
    description="사용자에게 새로운 추천을 생성합니다. 알고리즘에 따라 가장 적합한 사용자를 추천합니다.",
    request=ReferralCreateSerializer,
    responses={
      201: OpenApiResponse(
        response=ReferralSerializer,
        description="추천 생성 성공",
      ),
      400: get_referral_validation_error_schema(),
      401: get_unauthorized_error_schema(),
      404: get_no_more_referrals_error_schema(),
      500: get_internal_server_error_schema(),
    },
  )
  def post(self, request):
    """새로운 추천 생성"""
    serializer = ReferralCreateSerializer(data=request.data)
    if not serializer.is_valid():
      raise ReferralValidationError(message="Invalid referral data", details=serializer.errors)

    algorithm_type = serializer.validated_data["algorithm_type"]

    # 추천 생성
    referral = ReferralService.create_referral(self.current_user, algorithm_type)

    if not referral:
      raise NoMoreReferralsError(
        message="No more referrals available",
        details={"algorithm_type": algorithm_type},
      )

    # 비동기로 추천 인사이트 생성 태스크 시작
    generate_referral_llm_messages.delay(referral.id)

    logger.info(
      "Triggered referral insights generation",
      referral_id=referral.id,
      user_id=self.current_user.id,
    )

    response_serializer = ReferralSerializer(referral, context={'request': request})
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
