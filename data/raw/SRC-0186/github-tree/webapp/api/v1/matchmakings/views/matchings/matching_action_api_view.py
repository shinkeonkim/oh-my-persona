from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.matchmakings.exceptions import MatchingValidationError
from api.v1.matchmakings.permissions import MatchingPermission
from api.v1.matchmakings.schemas.error_schemas import (
    get_matching_not_found_error_schema,
    get_matching_validation_error_schema,
)
from api.v1.matchmakings.serializers import MatchingActionSerializer, MatchingSerializer
from api.v1.matchmakings.services import MatchingService
from api.v1.matchmakings.views.base_matchmaking_api_view import BaseMatchmakingAPIView
from common.schemas.error_schemas import (
    get_internal_server_error_schema,
    get_unauthorized_error_schema,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


@extend_schema(tags=["매칭"])
class MatchingActionAPIView(UpdateAPIView, BaseMatchmakingAPIView):
    """매칭 액션 처리 전용 뷰"""

    permission_classes = [IsAuthenticated, MatchingPermission]
    lookup_field = "id"
    lookup_url_kwarg = "matching_id"

    @extend_schema(
        operation_id="matching_action",
        summary="호감 승인/거부",
        description="받은 호감을 승인하거나 거부합니다.",
        request=MatchingActionSerializer,
        responses={
            200: OpenApiResponse(
                response=MatchingSerializer,
                description="호감 액션 처리 성공",
            ),
            400: get_matching_validation_error_schema(),
            401: get_unauthorized_error_schema(),
            404: get_matching_not_found_error_schema(),
            500: get_internal_server_error_schema(),
        },
    )
    def get_queryset(self):
        """매칭 쿼리셋 반환"""
        from matchmakings.models import Matching

        return Matching.objects.select_related("sender__profile__job_info", "receiver__profile__job_info")

    def get_serializer_class(self):
        """시리얼라이저 클래스 반환"""
        return MatchingActionSerializer

    def update(self, request, *args, **kwargs):
        """호감 승인/거부 처리"""
        matching = self.get_object()

        # 액션 데이터 검증
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise MatchingValidationError(message="Invalid action data", details=serializer.errors)

        action = serializer.validated_data["action"]

        # 액션 처리
        updated_matching = MatchingService.process_matching_action(matching, action)

        response_serializer = MatchingSerializer(updated_matching)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
