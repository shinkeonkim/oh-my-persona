from rest_framework import permissions

from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import ForbiddenError


class ConfirmedUserPermission(permissions.BasePermission):
    """
    승인된 사용자만 접근 가능한 Permission
    - confirmed_at이 null이 아닌 사용자만 접근 허용
    - 승인되지 않은 사용자는 403 Forbidden 반환
    """

    def has_permission(self, request, view):
        """
        사용자가 승인되었는지 확인
        """
        # 인증되지 않은 사용자는 기본 인증 체크에서 걸러짐
        if not request.user.is_authenticated:
            return False

        # 사용자가 승인되지 않은 경우
        if not request.user.is_confirmed:
            raise ForbiddenError(
                message="User not confirmed",
                details={
                    "error_code": ErrorCodes.USER_NOT_CONFIRMED.code,
                    "message": "사용자 승인이 완료되지 않았습니다. 관리자 승인 후 이용해주세요.",
                },
            )

        return True

    def has_object_permission(self, request, view, obj):
        """
        객체 레벨에서도 승인 확인
        """
        return self.has_permission(request, view)
