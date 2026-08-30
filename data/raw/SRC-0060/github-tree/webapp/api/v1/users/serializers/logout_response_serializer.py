from rest_framework import serializers


class LogoutResponseSerializer(serializers.Serializer):
  """
    Serializer for logout response.
    """

  message = serializers.CharField(help_text="Success message")
