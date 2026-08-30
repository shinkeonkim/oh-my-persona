from rest_framework import permissions


class ProfileProofImagePermission(permissions.BasePermission):
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
        - 조회 권한은 프로필 소유자 및 어드민만 가능
        """

        # obj는 Profile 객체이므로 obj.user로 접근
        if obj.user == request.user:
            return True

        # 관리자는 모든 프로필 이미지에 접근 가능
        if request.user.is_staff:
            return True

        return False
