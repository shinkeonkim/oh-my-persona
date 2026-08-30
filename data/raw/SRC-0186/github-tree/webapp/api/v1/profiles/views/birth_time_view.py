from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import BirthTimeSerializer


@extend_schema(tags=["프로필 데이터"])
class BirthTimeListView(APIView):
    """
    자동완성을 위한 모든 출생시 선택지를 나열합니다.
    """

    @extend_schema(
        operation_id="list_birth_times",
        summary="출생시 선택지 목록",
        description="자동완성 기능을 위한 모든 출생시 선택지(12지지)를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=BirthTimeSerializer(many=True),
                description="출생시 선택지 목록",
            )
        },
    )
    def get(self, request, *args, **kwargs):
        """모든 출생시 선택지 조회"""
        choices_data = BirthTimeSerializer.get_choices_data()
        return Response(choices_data)
