from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.views.base_api_view import BaseAPIView
from saju.services import TodaySajuScoreService


@extend_schema(
    tags=["사주"],
    summary="Today's Saju scores",
    description="API view to get today's Saju scores based on birth information.",
)
class TodaySajuScoreAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        birth_datetime = self.current_user_profile.birth_datetime()
        gender = self.current_user_profile.gender

        return Response(
            TodaySajuScoreService.get_today_saju_scores_from_birth(birth_datetime=birth_datetime, gender=gender)
        )
