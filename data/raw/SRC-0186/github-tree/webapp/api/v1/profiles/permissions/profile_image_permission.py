from rest_framework import permissions

from .profile_access_permission import ProfileAccessPermission


class ProfileImagePermission(permissions.BasePermission):
    """
    Custom permission for Profile Image operations.
    - Allows read and update operations for authenticated users on their own profile image
    - Denies delete operations
    - Requires user confirmation
    - For other users' profile images, requires referral/matching relationship
    """

    def has_permission(self, request, view):
        """
        Return True if permission is granted, False otherwise.
        """
        # Only authenticated users can access profile images
        if request.user.is_anonymous:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        - 생성 / 수정 /삭제 권한은 프로필 소유자만 가능
        - 조회 권한은 매칭된 프로필 소유자 / 어드민 / 프로필 소유자만 가능
        """
        # 자신의 프로필 이미지는 항상 접근 가능
        if obj.profile.user == request.user:
            return True

        # 관리자는 모든 프로필 이미지에 접근 가능
        if request.user.is_staff:
            return True

        # 다른 사용자의 프로필 이미지 접근 권한 확인
        if request.method in permissions.SAFE_METHODS:
            profile_access_permission = ProfileAccessPermission()
            try:
                return profile_access_permission.has_object_permission(request, view, obj.profile)
            except Exception:
                # ProfileAccessPermission에서 예외가 발생하면 접근 거부
                return False

        return False
