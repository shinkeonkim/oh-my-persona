from rest_framework import serializers


class TokenRefreshResponseSerializer(serializers.Serializer):
  """
    Serializer for token refresh response.
    """

  access = serializers.CharField(help_text="New JWT access token")
  refresh = serializers.CharField(required=False, help_text="New JWT refresh token (if rotation enabled)")
