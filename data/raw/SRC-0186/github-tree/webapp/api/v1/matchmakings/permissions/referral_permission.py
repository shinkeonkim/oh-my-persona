from rest_framework import permissions

from api.v1.profiles.permissions import ConfirmedUserPermission
from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import ForbiddenError


class ReferralPermission(permissions.BasePermission):
    """
    추천 현황 접근 권한 확인
    - 추천 현황 소유자만 접근 가능
    - 전체 목록에 대해선 승인된 사용자만 접근 가능 (ConfirmedUserPermission)
    """

    def has_permission(self, request, view):
        """
        추천 현황 권한 확인
        """
        user_permission = ConfirmedUserPermission()
        return user_permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        추천 현황 객체 권한 확인
        """
        user_permission = ConfirmedUserPermission()

        # 먼저 사용자 권한 확인
        if not user_permission.has_object_permission(request, view, obj):
            return False

        # 추천 현황 소유자만 접근 가능
        if obj.user != request.user:
            raise ForbiddenError(
                message="Referral matching access denied",
                details={
                    "error_code": ErrorCodes.MTM_403.code,
                    "message": "해당 추천 현황에 접근할 권한이 없습니다.",
                },
            )
        return True
