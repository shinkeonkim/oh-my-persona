from drf_spectacular.utils import OpenApiResponse, extend_schema
from reports.authentication import ReportBotAuthentication
from reports.models import Report, ReportPin
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.v1.reports.serializers import ReportDetailSerializer, ReportPinVerificationSerializer
from common.exceptions.not_found_error import NotFoundError
from common.exceptions.validation_error import ValidationError
from common.permissions.active_user_permission import ActiveUserPermission
from common.views import BaseAPIView


@extend_schema(tags=["레포트"])
class ReportDetailAPIView(BaseAPIView):
    authentication_classes = [
        JWTAuthentication,
        ReportBotAuthentication,
    ]
    permission_classes = [ActiveUserPermission]

    @extend_schema(
        operation_id="post_report_detail",
        summary="레포트 상세 조회",
        description="특정 아동에 대한 레포트 상세 정보를 조회합니다. JWT 인증 사용 시 PIN 번호가 필요하며, Bot 인증 사용 시 PIN 검증을 건너뜁니다.",
        request=ReportPinVerificationSerializer,
        responses={
            200: OpenApiResponse(
                response=ReportDetailSerializer,
                description="레포트 조회 성공",
            ),
            400: OpenApiResponse(description="잘못된 PIN 번호"),
            404: OpenApiResponse(description="레포트를 찾을 수 없음"),
        },
    )
    def post(self, request):
        """레포트 상세 조회 (PIN 인증)"""
        # JWT 인증일 경우에만 PIN 검증 진행
        if not isinstance(request.successful_authenticator, ReportBotAuthentication):
            try:
                report_pin = ReportPin.objects.get(user=request.user)

                # PIN이 설정되어 있으면 검증 수행
                pin_serializer = ReportPinVerificationSerializer(data=request.data)
                pin_serializer.is_valid(raise_exception=True)

                pin = pin_serializer.validated_data["pin"]
                if not report_pin.verify_pin(pin):
                    raise ValidationError(message="잘못된 PIN 번호입니다.")
            except ReportPin.DoesNotExist:
                # PIN이 설정되지 않은 경우 검증 스킵
                pass

        # 아동 확인
        user = request.user
        try:
            child = user.child
        except Exception:
            raise NotFoundError(message="등록된 자녀 정보가 없습니다.")

        # 레포트 조회
        try:
            report = (
                Report.objects.select_related("child", "user")
                .prefetch_related(
                    "game_reports",
                    "game_reports__game",
                    "game_reports__advices",
                    "game_reports__last_reflected_session",
                )
                .get(user=request.user, child=child)
            )
        except Report.DoesNotExist:
            raise NotFoundError(message="레포트를 찾을 수 없습니다.")

        serializer = ReportDetailSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
