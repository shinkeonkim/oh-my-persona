from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from api.v1.matchmakings.permissions import MatchingPermission
from api.v1.matchmakings.serializers import CompletedMatchingListSerializer
from api.v1.matchmakings.services import MatchingService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.pagination.standard_pagination import StandardPagination
from common.schemas.error_schemas import get_unauthorized_error_schema
from common.utils.logger import get_logger

logger = get_logger(__name__)


@extend_schema(tags=["매칭"])
class CompletedMatchingListAPIView(BaseMatchmakingAPIView, ListAPIView):
    """매칭 완료 목록 조회 전용 뷰"""

    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated, MatchingPermission]

    @extend_schema(
        operation_id="get_completed_matchings",
        summary="매칭 완료 목록 조회",
        description="""
        양쪽 모두 수락하여 매칭이 완료된 목록을 조회합니다.

        **조건:**
        - received_at이 NULL이 아닌 경우 (상대방이 수락한 경우)
        - 보낸 호감, 받은 호감 모두 포함
        """,
        responses={
            200: OpenApiResponse(
                response=CompletedMatchingListSerializer(many=True),
                description="매칭 완료 목록 조회 성공",
            ),
            401: get_unauthorized_error_schema(),
        },
    )
    def get_queryset(self):
        """매칭 완료 쿼리셋 반환"""
        return MatchingService.get_completed_matchings(self.current_user)

    def get_serializer_class(self):
        """시리얼라이저 클래스 반환"""
        return CompletedMatchingListSerializer
