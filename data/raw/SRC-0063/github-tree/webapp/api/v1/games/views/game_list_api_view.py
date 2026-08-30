from drf_spectacular.utils import OpenApiResponse, extend_schema
from games.models import Game
from rest_framework import status
from rest_framework.response import Response

from api.v1.games.serializers import GameListSerializer
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView


@extend_schema(tags=["게임"])
class GameListAPIView(BaseAPIView):
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="list_active_games",
        summary="활성화된 게임 목록 조회",
        description="현재 활성화되어 있는 게임들의 목록을 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=GameListSerializer(many=True),
                description="게임 목록 조회 성공",
            ),
        },
    )
    def get(self, request):
        """
        활성화된 게임 목록 조회
        """
        games = Game.objects.active().order_by("id")
        serializer = GameListSerializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
