from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from api.v1.matchmakings.permissions import MatchingPermission
from api.v1.matchmakings.serializers import MatchingListSerializer
from api.v1.matchmakings.services import MatchingService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.pagination.standard_pagination import StandardPagination
from common.schemas.error_schemas import get_unauthorized_error_schema
from common.utils.logger import get_logger

logger = get_logger(__name__)


@extend_schema(tags=["매칭"])
class SentMatchingListAPIView(BaseMatchmakingAPIView, ListAPIView):
    """보낸 호감 목록 조회 전용 뷰"""

    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated, MatchingPermission]

    @extend_schema(
        operation_id="get_sent_matchings",
        summary="보낸 호감 목록 조회 (진행 중)",
        description="""
        사용자가 보낸 호감(매칭) 중 진행 중인 목록을 조회합니다.

        **포함 조건:**
        - 보낸 호감 중 아직 응답이 없는 경우 (received_at, rejected_at 모두 NULL)

        **제외 조건:**
        - 매칭이 완료된 경우 → 매칭 완료 API 참조
        - 거절되거나 자동 거절된 경우 → 지난 인연 API 참조
        """,
        responses={
            200: OpenApiResponse(
                response=MatchingListSerializer(many=True),
                description="보낸 호감 목록 조회 성공",
            ),
            401: get_unauthorized_error_schema(),
        },
    )
    def get_queryset(self):
        """보낸 매칭 쿼리셋 반환"""
        return MatchingService.get_sent_matchings(self.current_user)

    def get_serializer_class(self):
        """시리얼라이저 클래스 반환"""
        return MatchingListSerializer
