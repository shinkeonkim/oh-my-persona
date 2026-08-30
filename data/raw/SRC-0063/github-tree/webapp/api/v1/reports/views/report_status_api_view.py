from drf_spectacular.utils import OpenApiResponse, extend_schema
from reports.authentication import ReportBotAuthentication
from reports.models import Report
from reports.services.report_status_check_service import ReportStatusCheckService
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.v1.reports.serializers import ReportStatusSerializer
from common.exceptions.not_found_error import NotFoundError
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView


@extend_schema(tags=["레포트"])
class ReportStatusAPIView(BaseAPIView):
    authentication_classes = [
        ReportBotAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ActiveUserPermission]
    serializer_class = ReportStatusSerializer

    @extend_schema(
        operation_id="get_report_status",
        summary="레포트 상태 조회",
        description="""
        특정 아동에 대한 레포트 생성 상태를 조회합니다.

        상태가 생성되지 않은 경우 자동으로 생성을 트리거하고 GENERATING 상태를 반환합니다.
        이후 다시 호출하면 업데이트된 상태(COMPLETED, ERROR 등)를 확인할 수 있습니다.
        """,
        responses={
            200: OpenApiResponse(
                response=ReportStatusSerializer,
                description="레포트 상태 조회 성공",
            ),
            404: OpenApiResponse(description="아동을 찾을 수 없음"),
        },
    )
    def post(self, request):
        """
        레포트 상태 체크 API

        - 상태 조회와 동시에 필요시 레포트 생성 트리거
        - ReportStatusCheckService를 통해 상태 확인 및 업데이트
        - 업데이트된 상태를 재조회하여 반환
        """

        # 아동 확인
        try:
            child = self.current_user.child
        except Exception:
            raise NotFoundError(message="등록된 자녀 정보가 없습니다.")

        # 레포트 조회 또는 생성
        report, _created = Report.objects.get_or_create_for_user_child(
            user=request.user,
            child=child,
        )

        # 상태 체크 및 필요시 생성 트리거
        status_service = ReportStatusCheckService(report)
        status_service.check_status()

        # 상태를 재조회하여 최신 상태 반환
        report.refresh_from_db()

        response_data = {
            "status": report.status,
            "description": report.get_status_display(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
