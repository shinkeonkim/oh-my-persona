from rest_framework import permissions

from common.exceptions.common_error_code import CommonErrorCode
from common.exceptions.forbidden_error import ForbiddenError


class ActiveUserPermission(permissions.BasePermission):
    """
    활성화된 사용자만 접근 가능한 Permission
    - is_active가 True인 사용자만 접근 허용
    - 비활성화된 사용자는 403 Forbidden 반환
    """

    def has_permission(self, request, _view):
        """
        사용자가 활성화되었는지 확인
        """
        # 인증되지 않은 사용자는 기본 인증 체크에서 걸러짐
        if not request.user.is_authenticated:
            return False

        # 사용자가 활성화되지 않은 경우
        if not request.user.is_active:
            raise ForbiddenError(
                message="계정이 비활성화 되었습니다. 관리자에게 문의해주세요.",
                details={
                    "error_code": CommonErrorCode.COMMON_403.code,
                },
            )

        return True

    def has_object_permission(self, request, view, _obj):
        """
        객체 레벨에서도 활성화 확인
        """
        return self.has_permission(request, view)
