from rest_framework import permissions

from common.enums.error_codes import ErrorCodes
from common.exceptions.custom_exceptions import ForbiddenError
from matchmakings.models import Matching, Referral


class ProfileAccessPermission(permissions.BasePermission):
    """
    프로필 접근 권한 Permission
    - 자신의 프로필: 항상 접근 가능
    - 다른 사용자의 프로필: 다음 경우에만 접근 가능
      1. 해당 프로필을 추천받은 경우 (Referral)
      2. 해당 프로필과 매칭을 생성한 경우 (Matching - 호감을 보낸 경우)
      3. 해당 프로필로부터 매칭을 받은 경우 (Matching - 호감을 받은 경우)
    """

    def has_permission(self, request, view):
        """
        기본 권한 확인
        """
        # 인증되지 않은 사용자는 기본 인증 체크에서 걸러짐
        if not request.user.is_authenticated:
            return False

        # 승인되지 않은 사용자는 ConfirmedUserPermission에서 걸러짐
        if not request.user.is_confirmed:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        특정 프로필 객체에 대한 접근 권한 확인
        """
        # 자신의 프로필은 항상 접근 가능
        if obj.user == request.user:
            return True

        # 다른 사용자의 프로필 접근 권한 확인
        return self._check_profile_access_permission(request.user, obj.user)

    def _check_profile_access_permission(self, current_user, target_user):
        """
        다른 사용자의 프로필 접근 권한 확인
        """
        # 1. 추천받은 경우 (Referral)
        if self._is_referred_user(current_user, target_user):
            return True

        # 2. 매칭을 생성한 경우 (호감을 보낸 경우)
        if self._is_matching_sender(current_user, target_user):
            return True

        # 3. 매칭을 받은 경우 (호감을 받은 경우)
        if self._is_matching_receiver(current_user, target_user):
            return True

        # 위 조건에 해당하지 않으면 접근 거부
        raise ForbiddenError(
            message="Profile access denied",
            details={
                "error_code": ErrorCodes.PROFILE_ACCESS_DENIED.code,
                "message": "해당 프로필에 접근할 권한이 없습니다. 추천받거나 매칭된 사용자의 프로필만 조회할 수 있습니다.",
            },
        )

    def _is_referred_user(self, current_user, target_user):
        """
        target_user를 추천받았는지 확인
        """
        return Referral.objects.filter(user=current_user, referral_user=target_user).exists()

    def _is_matching_sender(self, current_user, target_user):
        """
        target_user에게 호감을 보낸 경우 확인
        """
        return Matching.objects.filter(sender=current_user, receiver=target_user).exists()

    def _is_matching_receiver(self, current_user, target_user):
        """
        target_user로부터 호감을 받은 경우 확인
        """
        return Matching.objects.filter(sender=target_user, receiver=current_user).exists()
