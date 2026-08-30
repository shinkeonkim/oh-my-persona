from rest_framework import serializers


class LogoutRequestSerializer(serializers.Serializer):
  """
    Serializer for logout request.
    """

  refresh = serializers.CharField(required=True, help_text="JWT refresh token to blacklist")
