from django.conf import settings

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.serializers import ReferralResetQuotaResponseSerializer
from api.v1.matchmakings.services import ReferralResetService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_unauthorized_error_schema,
    get_validation_error_schema,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)

REFERRAL_QUOTA_RESET_TICKET_COST = settings.REFERRAL_QUOTA_RESET_TICKET_COST


@extend_schema(tags=["추천"])
class ResetReferralQuotaAPIView(BaseMatchmakingAPIView):
    """추천 횟수 초기화 API 뷰"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="reset_referral_quota",
        summary="추천 횟수 초기화",
        description=f"""
        사용자의 추천 횟수를 초기화합니다.

        **조건:**
        - 추천 가능 횟수가 0이어야 합니다.
        - {REFERRAL_QUOTA_RESET_TICKET_COST}개 이상의 티켓이 필요합니다.

        **처리:**
        - 티켓 {REFERRAL_QUOTA_RESET_TICKET_COST}개를 차감합니다.
        - 추천 횟수를 최대치로 초기화합니다.
        - TicketLog에 기록됩니다.
        """,
        request=None,
        responses={
            200: OpenApiResponse(
                response=ReferralResetQuotaResponseSerializer,
                description="추천 횟수 초기화 성공",
            ),
            401: get_unauthorized_error_schema(),
            422: get_validation_error_schema(),
            500: get_internal_server_error_schema(),
        },
    )
    def post(self, request):
        """추천 횟수 초기화"""
        user = ReferralResetService.reset_referral_quota(self.current_user)

        response_data = {
            "message": "추천 횟수가 초기화되었습니다.",
            "remaining_referral_quota": user.remaining_referral_quota,
            "ticket_amount": user.ticket_amount,
            "used_tickets": REFERRAL_QUOTA_RESET_TICKET_COST,
        }

        serializer = ReferralResetQuotaResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
