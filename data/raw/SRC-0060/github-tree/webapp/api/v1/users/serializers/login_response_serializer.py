from rest_framework import serializers

from .user_detail_serializer import UserDetailSerializer


class LoginResponseSerializer(serializers.Serializer):
  """
    Serializer for login response (JWT tokens + user info).
    """

  access = serializers.CharField(help_text="JWT access token")
  refresh = serializers.CharField(help_text="JWT refresh token")
  user = UserDetailSerializer(help_text="User information")
