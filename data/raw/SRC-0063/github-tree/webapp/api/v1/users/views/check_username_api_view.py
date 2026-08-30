from django.contrib.auth import get_user_model

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .base_user_api_view import BaseUserAPIView

User = get_user_model()


class CheckUsernameAPIView(BaseUserAPIView):
    """
    username 중복 여부를 확인하는 API View
    """

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="확인할 username",
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "exists": {
                        "type": "boolean",
                        "description": "username이 이미 사용 중인지 여부",
                    },
                },
            },
        },
        summary="Username 중복 확인",
        description="회원가입 시 username이 이미 사용 중인지 확인합니다.",
        tags=["Users"],
    )
    def get(self, request):
        username = request.query_params.get("username")

        if not username:
            return Response(
                {"error": "username parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exists = User.objects.filter(username=username).exists()

        return Response(
            {"exists": exists},
            status=status.HTTP_200_OK,
        )
