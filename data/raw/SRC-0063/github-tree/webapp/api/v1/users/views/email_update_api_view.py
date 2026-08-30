from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import EmailUpdateSerializer, UserDetailSerializer
from .base_user_api_view import BaseUserAPIView


class EmailUpdateAPIView(BaseUserAPIView):
    """
    사용자의 email을 수정하는 API View
    """

    permission_classes = [IsAuthenticated]
    serializer_class = EmailUpdateSerializer

    @extend_schema(
        request=EmailUpdateSerializer,
        responses={200: UserDetailSerializer},
        summary="사용자 이메일 수정",
        description="로그인한 사용자의 이메일을 수정합니다.",
        tags=["Users"],
    )
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.email = serializer.validated_data["email"]
        user.save()

        return Response(
            UserDetailSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
