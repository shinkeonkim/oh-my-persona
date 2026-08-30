from django.db import transaction
from django.http import Http404
from django.utils import timezone

from drf_spectacular.utils import OpenApiResponse, extend_schema
from games.choices.game_code_choice import GameCodeChoice
from games.choices.game_session_status_choice import GameSessionStatusChoice
from games.models import Game, GameResult, GameSession
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.v1.games.serializers import (
    BBStarFinishResponseSerializer,
    BBStarFinishSerializer,
    BBStarStartSerializer,
    GameStartResponseSerializer,
)
from common.exceptions.not_found_error import NotFoundError
from common.exceptions.validation_error import ValidationError
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView


@extend_schema(tags=["게임 - 뿅뿅 아기별"])
class BBStarStartAPIView(BaseAPIView):
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="start_bb_star_game",
        summary="뿅뿅 아기별 게임 시작",
        description=(
            "뿅뿅 아기별 게임 세션을 시작합니다.\n\n"
            "**게임 설명:**\n"
            "- 깜빡이는 별의 순서를 기억하고 올바른 순서로 클릭하는 게임\n"
            "- 최대 10라운드까지 진행되며, 각 라운드마다 별의 개수가 증가\n"
            "- 시간 제한이 있으며, 시간 내에 올바른 순서로 클릭해야 함\n\n"
            "**응답 필드:**\n"
            "- `session_id`: 게임 종료 API 호출 시 필요한 세션 ID (UUID)\n"
            "- `game_code`: 게임 코드 ('BB_STAR')\n"
            "- `started_at`: 게임 시작 시각\n"
            "- `status`: 세션 상태 ('STARTED')\n\n"
            "**주의사항:**\n"
            "- 게임 종료 API 호출 시 반드시 이 API에서 받은 `session_id`를 사용해야 함"
        ),
        request=BBStarStartSerializer,
        responses={
            201: OpenApiResponse(
                response=GameStartResponseSerializer,
                description="게임 세션 시작 성공. `session_id`를 저장하여 게임 종료 시 사용",
            ),
            404: OpenApiResponse(description="게임(뿅뿅 아기별)이 활성화되어 있지 않거나 아이를 찾을 수 없습니다."),
        },
    )
    def post(self, request):
        serializer = BBStarStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            game = get_object_or_404(Game.objects.by_code(GameCodeChoice.BB_STAR))
        except Http404:
            raise NotFoundError(message="게임( BB_STAR, 뿅뿅 아기별 게임 )이 활성화되어 있지 않습니다.")

        if not hasattr(request.user, "child"):
            raise NotFoundError(message="등록된 자녀 정보가 없습니다.")
        child = request.user.child

        session = GameSession.objects.create(
            parent=request.user,
            child=child,
            game=game,
            status=GameSessionStatusChoice.STARTED,
            started_at=timezone.now(),
        )

        return Response(
            {
                "session_id": str(session.id),
                "game_code": game.code,
                "started_at": session.started_at,
                "status": session.status,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["게임 - 뿅뿅 아기별"])
class BBStarFinishAPIView(BaseAPIView):
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="finish_bb_star_game",
        summary="뿅뿅 아기별 게임 종료",
        description=(
            "뿅뿅 아기별 게임 세션을 종료하고 결과 저장\n\n"
            "**요청 필드:**\n"
            "- `session_id` (필수): 게임 시작 API에서 받은 세션 ID (UUID)\n"
            "- `score` (필수): 게임 전체 총 점수\n"
            "- `wrong_count` (선택): 게임 전체 틀린 개수 (기본값: 0)\n"
            "- `round_count` (선택): 게임 전체 라운드 수 (최대 10)\n"
            "- `success_count` (선택): 게임 전체 성공한 라운드 수\n"
            "- `meta` (선택): 라운드별 상세 데이터\n\n"
            "**meta 필드 구조:**\n"
            "```json\n"
            "{\n"
            '  "round_details": [\n'
            "    {\n"
            '      "round_number": 1,\n'
            '      "score": 5,\n'
            '      "wrong_count": 0,\n'
            '      "is_success": true,\n'
            '      "time_limit_exceeded": false\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "**주의사항:**\n"
            "- 뿅뿅아기별 게임은 시간 측정이 없으므로 `reaction_ms_sum` 필드를 보내지 않음\n"
            "- `meta.round_details`의 각 라운드에도 `reaction_ms_sum` 필드가 없음\n"
            "- 동일한 세션을 두 번 종료하려고 하면 422 에러가 발생"
        ),
        request=BBStarFinishSerializer,
        responses={
            200: OpenApiResponse(
                response=BBStarFinishResponseSerializer,
                description=(
                    "게임 세션 종료 성공. 저장된 게임 결과를 반환\n\n"
                    "**응답 필드:**\n"
                    "- `session_id`: 게임 세션 ID\n"
                    "- `game_code`: 게임 코드 ('BB_STAR')\n"
                    "- `score`: 게임 전체 총 점수\n"
                    "- `wrong_count`: 게임 전체 틀린 개수\n"
                    "- `round_count`: 게임 전체 라운드 수\n"
                    "- `success_count`: 게임 전체 성공한 라운드 수\n"
                    "- `meta`: 라운드별 상세 데이터 (시간 관련 필드 없음)"
                ),
            ),
            404: OpenApiResponse(description="세션을 찾을 수 없거나 접근 권한이 없습니다."),
            422: OpenApiResponse(description="이미 완료된 세션입니다."),
        },
    )
    def post(self, request):
        serializer = BBStarFinishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            try:
                session = (
                    GameSession.objects.select_related("child", "game")
                    .select_for_update()
                    .get(id=data["session_id"], parent=request.user)
                )
            except GameSession.DoesNotExist:
                raise NotFoundError(message="세션을 찾을 수 없거나 접근 권한이 없습니다.")

            if session.status == GameSessionStatusChoice.COMPLETED:
                raise ValidationError(message="이미 완료된 세션입니다.")

            session.status = GameSessionStatusChoice.COMPLETED
            session.ended_at = timezone.now()
            session.save(update_fields=["status", "ended_at"])

            result = GameResult.objects.create(
                session=session,
                child=session.child,
                game=session.game,
                score=data["score"],
                wrong_count=data.get("wrong_count", 0),
                reaction_ms_sum=data.get("reaction_ms_sum"),
                round_count=data.get("round_count"),
                success_count=data.get("success_count"),
                meta=data.get("meta", {}),
            )

        return Response(
            {
                "session_id": str(session.id),
                "game_code": session.game.code,
                "score": result.score,
                "wrong_count": result.wrong_count,
                "round_count": result.round_count,
                "success_count": result.success_count,
                "meta": result.meta or {},
            },
            status=status.HTTP_200_OK,
        )
