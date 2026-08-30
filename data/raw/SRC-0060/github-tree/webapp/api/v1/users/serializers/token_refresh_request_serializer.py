from rest_framework import serializers


class TokenRefreshRequestSerializer(serializers.Serializer):
  """
    Serializer for token refresh request.
    """

  refresh = serializers.CharField(required=True, help_text="JWT refresh token to exchange for new access token")
