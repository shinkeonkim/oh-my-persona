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
    GameStartResponseSerializer,
    KidsTrafficFinishResponseSerializer,
    KidsTrafficFinishSerializer,
    KidsTrafficStartSerializer,
)
from common.exceptions.not_found_error import NotFoundError
from common.exceptions.validation_error import ValidationError
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView


@extend_schema(tags=["게임 - 꼬마 교통지킴이"])
class KidsTrafficStartAPIView(BaseAPIView):
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="start_kids_traffic_game",
        summary="꼬마 교통지킴이 게임 시작",
        description=(
            "꼬마 교통지킴이 게임 세션을 시작합니다.\n\n"
            "**게임 설명:**\n"
            "- 신호등 게임으로, 빨간불/초록불에 맞춰 '멈춰!'/'달려!' 버튼을 누르는 게임\n"
            "- 최대 10라운드까지 진행되며, 각 라운드마다 신호등 변화 속도가 빨라짐\n"
            "- 신호등에 맞지 않는 버튼을 누르면 실패 횟수가 증가하며, 3회 실패 시 게임 종료\n"
            "- 반응 시간을 측정하여 집중력과 반응 속도를 평가\n\n"
            "**응답 필드:**\n"
            "- `session_id`: 게임 종료 API 호출 시 필요한 세션 ID (UUID)\n"
            "- `game_code`: 게임 코드 ('KIDS_TRAFFIC')\n"
            "- `started_at`: 게임 시작 시각\n"
            "- `status`: 세션 상태 ('STARTED')\n\n"
            "**주의사항:**\n"
            "- 게임 종료 API 호출 시 반드시 이 API에서 받은 `session_id`를 사용해야함"
        ),
        request=KidsTrafficStartSerializer,
        responses={
            201: OpenApiResponse(
                response=GameStartResponseSerializer,
                description="게임 세션 시작 성공. `session_id`를 저장하여 게임 종료 시 사용",
            ),
            404: OpenApiResponse(description="게임(꼬마 교통지킴이)이 활성화되어 있지 않거나 아이를 찾을 수 없습니다."),
        },
    )
    def post(self, request):
        serializer = KidsTrafficStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            game = get_object_or_404(Game.objects.by_code(GameCodeChoice.KIDS_TRAFFIC))
        except Http404:
            raise NotFoundError(message="게임( KIDS_TRAFFIC, 꼬마 교통지킴이 )이 활성화되어 있지 않습니다.")

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


@extend_schema(tags=["게임 - 꼬마 교통지킴이"])
class KidsTrafficFinishAPIView(BaseAPIView):
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="finish_kids_traffic_game",
        summary="꼬마 교통지킴이 게임 종료",
        description=(
            "꼬마 교통지킴이 게임 세션을 종료하고 결과 저장\n\n"
            "**요청 필드:**\n"
            "- `session_id` (필수): 게임 시작 API에서 받은 세션 ID (UUID)\n"
            "- `score` (필수): 게임 전체 총 점수\n"
            "- `wrong_count` (선택): 게임 전체 틀린 개수 (기본값: 0)\n"
            "- `reaction_ms_sum` (선택): 게임 전체 반응시간 합계 (밀리초 단위)\n"
            "- `round_count` (선택): 게임 전체 라운드 수 (최대 10)\n"
            "- `success_count` (선택): 게임 전체 성공한 라운드 수\n"
            "- `meta` (선택): 라운드별 상세 데이터\n\n"
            "**meta 필드 구조:**\n"
            "```json\n"
            "{\n"
            '  "round_details": [\n'
            "    {\n"
            '      "round_number": 1,\n'
            '      "score": 3,\n'
            '      "wrong_count": 0,\n'
            '      "reaction_ms_sum": 1500,\n'
            '      "is_success": true,\n'
            '      "time_limit_exceeded": false\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "**주의사항:**\n"
            "- 교통지킴이 게임은 반응 시간 측정이 중요하므로 `reaction_ms_sum` 필드를 포함하는 것을 권장\n"
            "- `meta.round_details`의 각 라운드에도 `reaction_ms_sum` 필드를 포함할 수 있음\n"
            "- 동일한 세션을 두 번 종료하려고 하면 422 에러가 발생"
        ),
        request=KidsTrafficFinishSerializer,
        responses={
            200: OpenApiResponse(
                response=KidsTrafficFinishResponseSerializer,
                description=(
                    "게임 세션 종료 성공. 저장된 게임 결과를 반환\n\n"
                    "**응답 필드:**\n"
                    "- `session_id`: 게임 세션 ID\n"
                    "- `game_code`: 게임 코드 ('KIDS_TRAFFIC')\n"
                    "- `score`: 게임 전체 총 점수\n"
                    "- `wrong_count`: 게임 전체 틀린 개수\n"
                    "- `reaction_ms_sum`: 게임 전체 반응시간 합계 (밀리초)\n"
                    "- `round_count`: 게임 전체 라운드 수\n"
                    "- `success_count`: 게임 전체 성공한 라운드 수\n"
                    "- `meta`: 라운드별 상세 데이터 (반응시간 정보 포함)"
                ),
            ),
            404: OpenApiResponse(description="세션을 찾을 수 없거나 접근 권한이 없습니다."),
            422: OpenApiResponse(description="이미 완료된 세션입니다."),
        },
    )
    def post(self, request):
        serializer = KidsTrafficFinishSerializer(data=request.data)
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
                "reaction_ms_sum": result.reaction_ms_sum,
                "round_count": result.round_count,
                "success_count": result.success_count,
                "meta": result.meta or {},
            },
            status=status.HTTP_200_OK,
        )
