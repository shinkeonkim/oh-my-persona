from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.permissions import MatchingPermission
from api.v1.matchmakings.schemas.error_schemas import (
    get_matching_access_denied_error_schema,
    get_matching_not_found_error_schema,
)
from api.v1.matchmakings.serializers import MatchingSerializer
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_unauthorized_error_schema,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


@extend_schema(tags=["매칭"])
class MatchingDetailAPIView(RetrieveAPIView, BaseMatchmakingAPIView):
    """매칭 상세 정보 조회 전용 뷰"""

    permission_classes = [IsAuthenticated, MatchingPermission]
    lookup_field = "id"
    lookup_url_kwarg = "matching_id"

    @extend_schema(
        operation_id="get_matching_detail",
        summary="매칭 상세 정보 조회",
        description="특정 매칭의 상세 정보를 조회합니다. 본인이 보낸 매칭이거나 받은 매칭만 조회 가능합니다.",
        responses={
            200: OpenApiResponse(
                response=MatchingSerializer,
                description="매칭 상세 정보 조회 성공",
            ),
            401: get_unauthorized_error_schema(),
            403: get_matching_access_denied_error_schema(),
            404: get_matching_not_found_error_schema(),
            500: get_internal_server_error_schema(),
        },
    )
    def get_queryset(self):
        """매칭 쿼리셋 반환"""
        from matchmakings.models import Matching

        return Matching.objects.select_related(
            "sender__profile__job_info",
            "receiver__profile__job_info",
            "referral__user__profile__job_info",
            "referral__referral_user__profile__job_info",
        )

    def get_serializer_class(self):
        """시리얼라이저 클래스 반환"""
        return MatchingSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        매칭 상세 정보 조회

        Args:
            request: HTTP 요청 객체
            matching_id: 조회할 매칭 ID

        Returns:
            Response: 매칭 상세 정보
        """
        matching = self.get_object()

        serializer = self.get_serializer(matching)

        return Response(serializer.data, status=status.HTTP_200_OK)
