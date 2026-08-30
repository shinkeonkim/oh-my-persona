from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.users.serializers import ChildSerializer
from common.views import BaseAPIView
from users.models.child import Child


class ChildAPIView(BaseAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        child = Child.objects.filter(parent=self.current_user).first()

        return child

    @extend_schema(
        operation_id="Get Child Info",
        description="자녀 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=ChildSerializer,
                description="자녀 정보 조회 성공",
            )
        },
    )
    def get(self, request):
        child = self.get_object()
        serializer = self.get_serializer(child)
        return Response(serializer.data)

    @extend_schema(
        operation_id="Update Child Info",
        description="자녀 정보를 수정합니다.",
        request=ChildSerializer,
        responses={
            200: OpenApiResponse(
                response=ChildSerializer,
                description="자녀 정보 수정 성공",
            )
        },
    )
    def post(self, request):
        child = self.get_object()

        serializer = self.get_serializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(parent=self.current_user)
        return Response(serializer.data)
