from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.response import Response

from api.v1.health_check.serializers import HealthCheckSerializer
from common.views import BaseAPIView


class HealthCheckAPIView(BaseAPIView):
    permission_classes = []

    @extend_schema(
        operation_id="health_check",
        tags=["Health Check"],
        summary="Application Health Check",
        description="Check the health status of the application.",
        request=None,
        responses={
            200: OpenApiResponse(
                response=HealthCheckSerializer,
                description="Application is healthy and running",
                examples=[
                    OpenApiExample(
                        name="Healthy response",
                        value={"status": "ok"},
                        status_codes=[200],
                    ),
                ],
            ),
        },
    )
    def get(self, _request):
        return Response({"status": "ok"})
