from django.utils import timezone

from drf_spectacular.utils import OpenApiResponse, extend_schema
from reports.models import ReportPin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.reports.serializers import SetReportPinRequestSerializer, SetReportPinResponseSerializer
from common.views import BaseAPIView


class SetReportPinAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SetReportPinRequestSerializer

    def get_object(self):
        report_pin = ReportPin.objects.filter(user=self.current_user).first()
        return report_pin

    @extend_schema(
        operation_id="Set Report Pin",
        description="레포트 핀을 설정합니다.",
        request=SetReportPinRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SetReportPinResponseSerializer,
                description="레포트 핀 설정 성공",
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pin = serializer.validated_data["pin"]
        report_pin = self.get_object()
        if not report_pin:
            report_pin = ReportPin(user=self.current_user)
        report_pin.pin_hash = report_pin.get_pin_hash(pin)
        report_pin.enabled_at = timezone.now()
        report_pin.save()

        response_serializer = SetReportPinResponseSerializer(
            {"is_success": True, "message": "Report pin set successfully."}
        )
        return Response(response_serializer.data)
