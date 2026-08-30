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
class PastConnectionListAPIView(BaseMatchmakingAPIView, ListAPIView):
    """지난 인연 목록 조회 전용 뷰"""

    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated, MatchingPermission]

    @extend_schema(
        operation_id="get_past_connections",
        summary="지난 인연 목록 조회",
        description="""
        거절되었거나 매칭이 성사되지 않은 지난 인연 목록을 조회합니다.

        **포함 조건:**
        - 호감을 보냈거나 받았지만 거절된 경우
        - 1주일이 지나 자동으로 거절된 경우
        - 보낸 호감, 받은 호감 모두 포함

        **제외 조건:**
        - 매칭이 완료된 경우 (received_at이 NULL이 아닌 경우)
        """,
        responses={
            200: OpenApiResponse(
                response=MatchingListSerializer(many=True),
                description="지난 인연 목록 조회 성공",
            ),
            401: get_unauthorized_error_schema(),
        },
    )
    def get_queryset(self):
        """지난 인연 쿼리셋 반환"""
        return MatchingService.get_past_connections(self.current_user)

    def get_serializer_class(self):
        """시리얼라이저 클래스 반환"""
        return MatchingListSerializer
