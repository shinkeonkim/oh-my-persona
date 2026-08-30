from django.conf import settings

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.exceptions import MatchingValidationError
from api.v1.matchmakings.permissions import MatchingPermission
from api.v1.matchmakings.schemas.error_schemas import (
    get_matching_validation_error_schema,
    get_referral_not_found_error_schema,
)
from api.v1.matchmakings.serializers import MatchingCreateSerializer, MatchingSerializer
from api.v1.matchmakings.services import MatchingService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_unauthorized_error_schema,
)
from common.utils.logger import get_logger

MATCHING_TICKET_COST = settings.MATCHING_TICKET_COST

logger = get_logger(__name__)


@extend_schema(tags=["매칭"])
class CreateMatchingAPIView(BaseMatchmakingAPIView):
    """매칭 생성 전용 뷰"""

    permission_classes = [IsAuthenticated, MatchingPermission]

    @extend_schema(
        operation_id="create_matching_from_referral",
        summary="추천으로부터 매칭 생성",
        description="추천받은 사용자에게 호감을 보내 매칭을 생성합니다. 티켓이 차감됩니다.",
        request=MatchingCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=MatchingSerializer,
                description="매칭 생성 성공",
            ),
            400: get_matching_validation_error_schema(),
            401: get_unauthorized_error_schema(),
            404: get_referral_not_found_error_schema(),
            500: get_internal_server_error_schema(),
        },
    )
    def post(self, request):
        """추천으로부터 매칭 생성"""
        # TODO: ticket 처리 관련 lock 필요
        serializer = MatchingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise MatchingValidationError(message="Invalid matching creation data", details=serializer.errors)

        referral_id = serializer.validated_data["referral_id"]
        required_ticket_amount = MATCHING_TICKET_COST

        # 티켓 보유량 확인
        if not MatchingService.check_ticket_availability(self.current_user, required_ticket_amount):
            raise MatchingValidationError(
                message="Insufficient tickets",
                details={
                    "required_tickets": required_ticket_amount,
                    "available_tickets": self.current_user.ticket_amount,
                },
            )

        # 매칭 생성
        matching = MatchingService.create_matching_from_referral(self.current_user, referral_id, required_ticket_amount)

        response_serializer = MatchingSerializer(matching)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
