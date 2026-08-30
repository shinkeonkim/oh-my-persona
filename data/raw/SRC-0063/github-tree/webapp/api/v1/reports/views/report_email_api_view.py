from django.conf import settings

from drf_spectacular.utils import OpenApiResponse, extend_schema
from reports.tasks.report_email_task import send_report_email_task
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.v1.reports.serializers import ReportEmailSerializer
from common.exceptions.not_found_error import NotFoundError
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView
from users.models import BotToken

FRONTEND_REPORT_URL = settings.FRONTEND_REPORT_URL


@extend_schema(tags=["레포트"])
class ReportEmailAPIView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="send_report_email",
        summary="레포트 이메일 전송",
        description="""
        레포트를 PDF로 생성하여 이메일로 전송합니다.

        - email 파라미터가 없으면 request.user.email을 사용합니다.
        - BOT 토큰을 자동으로 생성하여 프론트엔드 URL에 첨부합니다.
        - PDF를 생성하고 지정된 이메일로 전송합니다.
        """,
        request=ReportEmailSerializer,
        responses={
            200: OpenApiResponse(
                description="이메일 전송 성공",
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="사용자 이메일이 없음"),
        },
    )
    def post(self, request):
        """
        레포트 PDF를 생성하여 이메일로 전송

        - BOT 토큰 생성
        - 프론트엔드 URL에 토큰 첨부
        - PDF 생성 및 이메일 전송
        """
        serializer = ReportEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 이메일 주소 결정 (요청 데이터 또는 사용자 이메일)
        to_email = serializer.validated_data.get("email") or request.user.email

        if not to_email:
            raise NotFoundError(message="이메일 주소가 제공되지 않았으며, 사용자 이메일도 없습니다.")

        # BOT 토큰 생성
        bot_token = BotToken.create_for_report(request.user)

        site_url = f"{FRONTEND_REPORT_URL}?BOT_TOKEN={bot_token.token}"

        send_report_email_task.delay(
            to_email=to_email,
            site_url=site_url,
            bot_token_id=bot_token.id,
        )

        return Response(
            {"message": "레포트 이메일 전송이 시작되었습니다."},
            status=status.HTTP_200_OK,
        )
