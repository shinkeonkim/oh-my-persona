from rest_framework import permissions

from api.v1.profiles.permissions import ConfirmedUserPermission
from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import ForbiddenError


class MatchingPermission(permissions.BasePermission):
    """
    매칭 접근 권한 확인
    - 매칭 송신자 또는 수신자만 접근 가능
    - 매칭 송신자와 수신자가 아닌 경우 접근 거부
    - 전체 목록에 대해선 승인된 사용자만 접근 가능 (ConfirmedUserPermission)
    """

    def has_permission(self, request, view):
        """
        매칭 권한 확인
        """
        user_permission = ConfirmedUserPermission()
        return user_permission.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """
        매칭 객체 권한 확인
        """
        user_permission = ConfirmedUserPermission()

        # 먼저 사용자 권한 확인
        if not user_permission.has_object_permission(request, view, obj):
            return False

        # 매칭 접근 권한 확인
        if obj.sender != request.user and obj.receiver != request.user:
            raise ForbiddenError(
                message="Matching access denied",
                details={
                    "error_code": ErrorCodes.MTM_403.code,
                    "message": "해당 매칭에 접근할 권한이 없습니다.",
                },
            )

        return True
