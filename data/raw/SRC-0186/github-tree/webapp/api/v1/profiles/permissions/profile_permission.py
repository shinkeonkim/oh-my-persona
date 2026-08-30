from rest_framework import permissions


class ProfilePermission(permissions.BasePermission):
    """
    Custom permission for Profile operations.
    - Allows read and update operations for authenticated users on their own profile
    - Denies delete operations
    """

    def has_permission(self, request, view):
        """
        Return True if permission is granted, False otherwise.
        """
        # Only authenticated users can access profiles
        if not request.user.is_authenticated:
            return False

        # Deny DELETE operations
        if request.method == "DELETE":
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted for the specific object, False otherwise.
        """
        # Only the profile owner can access their profile
        if obj.user != request.user:
            return False

        # Deny DELETE operations at object level as well
        if request.method == "DELETE":
            return False

        return True
