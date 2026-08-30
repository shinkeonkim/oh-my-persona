from rest_framework.permissions import IsAuthenticated

from api.v1.profiles.permissions import ConfirmedUserPermission
from common.views import BaseAPIView


class BaseMatchmakingAPIView(BaseAPIView):
    """매칭 관련 API의 기본 뷰 클래스"""

    permission_classes = [IsAuthenticated, ConfirmedUserPermission]
